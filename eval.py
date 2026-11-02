"""Evaluate the extractor against hand-reconciled labels.

Usage:
    python eval.py run      # call Bedrock on every labeled posting (skips cached ones)
    python eval.py score    # score cached predictions against labels, write results/report.md
"""
import json
import os
import re
import sys
import time

LABELS_DIR = "labels"
POSTINGS_DIR = "postings"
PRED_DIR = "results/predictions"
REPORT = "results/report.md"

# us. inference profile pricing (USD per 1M tokens). Verify on the AWS pricing page.
PRICE_IN, PRICE_OUT = 0.33, 2.75

SINGLE_FIELDS = ["company", "role_title", "location", "work_mode", "term", "deadline"]
LIST_FIELDS = ["required_skills", "nice_to_have_skills"]

# Different spellings of the same skill. Both sides are mapped to the right-hand name.
ALIASES = {
    "azure": "microsoft azure",
    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "vs code": "vscode",
    "visual studio code": "vscode",
    "spring": "spring framework",
    "node": "node.js",
    "nodejs": "node.js",
    "postgres": "postgresql",
    "dynamo": "dynamodb",
    "javascripts": "javascript",
    "ready api": "readyapi",
    "ms office": "microsoft office",
    "microsoft office suite": "microsoft office",
    "llm": "llms",
    "large language models": "llms",
    "rest api": "rest apis",
    "restful apis": "rest apis",
    "ci/cd pipeline": "ci/cd",
    "ci/cd pipelines": "ci/cd",
    "oop": "object oriented programming",
    "object-oriented programming": "object oriented programming",
    "elastic search": "elasticsearch",
    "springboot": "spring boot",
}


# ---------- running the model ----------

def run():
    from extractor import USAGE, extract, grounding_check  # imported here so `score` needs no AWS

    os.makedirs(PRED_DIR, exist_ok=True)
    for name in sorted(f[:-5] for f in os.listdir(LABELS_DIR) if f.endswith(".json")):
        out_path = os.path.join(PRED_DIR, name + ".json")
        if os.path.exists(out_path):
            print(f"{name}: cached, skipping")
            continue
        with open(os.path.join(POSTINGS_DIR, name + ".txt")) as f:
            posting = f.read()
        USAGE.clear()
        record = {"usage": None, "error": None, "prediction": None}
        try:
            record["prediction"] = grounding_check(extract(posting), posting)
        except Exception as e:  # keep going; a failed posting is scored as all-wrong
            record["error"] = str(e)
        record["usage"] = list(USAGE)  # one entry per model call (2 if it retried)
        with open(out_path, "w") as f:
            json.dump(record, f, indent=2)
        print(f"{name}: {'ERROR ' + record['error'] if record['error'] else 'ok'} "
              f"({len(USAGE)} call(s))")
        time.sleep(1)  # be gentle with Bedrock rate limits


# ---------- scoring ----------

def norm_text(s):
    if s is None:
        return None
    s = s.replace("–", "-").replace("—", "-").lower()
    s = re.sub(r"\s+", " ", s).strip(" .,;:")
    return s or None


def norm_skill(s):
    s = norm_text(s)
    return ALIASES.get(s, s)


def flat(pred):
    """Turn the model's {value, quote, grounded} output into the label format."""
    out = {f: (pred.get(f) or {}).get("value") for f in SINGLE_FIELDS}
    for f in LIST_FIELDS:
        out[f] = [i.get("value") for i in pred.get(f) or [] if i.get("value")]
    return out


def prf(tp, n_pred, n_true):
    p = tp / n_pred if n_pred else 1.0
    r = tp / n_true if n_true else 1.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f1


def score():
    names = sorted(f[:-5] for f in os.listdir(LABELS_DIR) if f.endswith(".json"))
    field_ok = {f: 0 for f in SINGLE_FIELDS}
    mismatches = []
    skills = {k: [0, 0, 0] for k in LIST_FIELDS + ["any_list"]}  # tp, n_pred, n_true
    flagged_total = flagged_wrong = 0
    fixes_total = errors = calls = tok_in = tok_out = 0
    latencies = []

    for name in names:
        with open(os.path.join(LABELS_DIR, name + ".json")) as f:
            truth = json.load(f)
        path = os.path.join(PRED_DIR, name + ".json")
        if not os.path.exists(path):
            sys.exit(f"No prediction for {name}. Run `python eval.py run` first.")
        with open(path) as f:
            rec = json.load(f)

        for u in rec["usage"]:
            calls += 1
            tok_in += u["input_tokens"]
            tok_out += u["output_tokens"]
            latencies.append(u["latency_ms"])

        if rec["error"]:
            errors += 1
            pred_raw = {}
        else:
            pred_raw = rec["prediction"]
            fixes_total += len(pred_raw.get("fixes", []))
        pred = flat(pred_raw)

        # Single fields: correct if equal after normalization (null == null counts).
        for fld in SINGLE_FIELDS:
            ok = norm_text(pred[fld]) == norm_text(truth[fld])
            field_ok[fld] += ok
            if not ok:
                mismatches.append(f"| {name} | {fld} | {truth[fld]} | {pred[fld]} |")
            item = pred_raw.get(fld) or {}
            if item.get("grounded") is False:
                flagged_total += 1
                flagged_wrong += not ok

        # Skills: set overlap per list, and ignoring which list (pure extraction).
        for fld in LIST_FIELDS:
            p = {norm_skill(s) for s in pred[fld]}
            t = {norm_skill(s) for s in truth[fld]}
            skills[fld][0] += len(p & t)
            skills[fld][1] += len(p)
            skills[fld][2] += len(t)
            true_all = {norm_skill(s) for s in truth[LIST_FIELDS[0]] + truth[LIST_FIELDS[1]]}
            for item in pred_raw.get(fld) or []:
                if item.get("grounded") is False:
                    flagged_total += 1
                    flagged_wrong += norm_skill(item.get("value") or "") not in true_all
        p_all = {norm_skill(s) for f in LIST_FIELDS for s in pred[f]}
        t_all = {norm_skill(s) for f in LIST_FIELDS for s in truth[f]}
        skills["any_list"][0] += len(p_all & t_all)
        skills["any_list"][1] += len(p_all)
        skills["any_list"][2] += len(t_all)

    n = len(names)
    cost = tok_in / 1e6 * PRICE_IN + tok_out / 1e6 * PRICE_OUT
    lat = sorted(latencies)
    lines = [
        f"# Evaluation results ({n} postings)\n",
        "## Fields (exact match after normalizing case, whitespace and dashes)\n",
        "| Field | Accuracy |", "|---|---|",
        *[f"| {f} | {field_ok[f]}/{n} ({field_ok[f] / n:.0%}) |" for f in SINGLE_FIELDS],
        "\n## Skills\n",
        "| List | Precision | Recall | F1 |", "|---|---|---|---|",
    ]
    for k, label in [("required_skills", "Required"), ("nice_to_have_skills", "Nice-to-have"),
                     ("any_list", "Any list (ignores required vs nice-to-have)")]:
        p, r, f1 = prf(*skills[k])
        lines.append(f"| {label} | {p:.0%} | {r:.0%} | {f1:.0%} |")
    lines += [
        "\n## Guardrails\n",
        f"- Items flagged by the grounding check: {flagged_total} "
        f"({flagged_wrong} of them actually wrong)",
        f"- Rule fixes applied in code: {fixes_total}",
        f"- Postings that failed after retry: {errors}",
        f"- Model calls: {calls} for {n} postings ({calls - n + errors} retries)",
        "\n## Cost and latency\n",
        f"- Tokens: {tok_in:,} in, {tok_out:,} out",
        f"- Estimated cost: ${cost:.4f} total, ${cost / n:.5f} per posting",
        f"- Latency per call: median {lat[len(lat) // 2] / 1000:.1f} s, "
        f"max {lat[-1] / 1000:.1f} s" if lat else "- Latency: n/a",
        "\n## Field mismatches (review by hand: some are wording, not errors)\n",
        "| Posting | Field | Label | Model |", "|---|---|---|---|",
        *mismatches,
    ]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:20]))
    print(f"\nFull report: {REPORT}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        run()
    elif cmd == "score":
        score()
    else:
        sys.exit(__doc__)