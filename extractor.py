import boto3
import copy
import json
import re
import sys

MODEL_ID = "us.amazon.nova-2-lite-v1:0"
REGION = "us-east-2"

client = boto3.client("bedrock-runtime", region_name=REGION)

SYSTEM_PROMPT = """You extract structured information from internship job postings.

Return ONLY a JSON object, with no other text, in exactly this shape:
{
  "company":             {"value": string or null, "quote": string or null},
  "role_title":          {"value": string or null, "quote": string or null},
  "location":            {"value": string or null, "quote": string or null},
  "work_mode":           {"value": "remote" or "hybrid" or "onsite" or null, "quote": string or null},
  "term":                {"value": string or null, "quote": string or null},
  "deadline":            {"value": string or null, "quote": string or null},
  "required_skills":     [{"value": string, "quote": string}],
  "nice_to_have_skills": [{"value": string, "quote": string}]
}

Rules:
- "quote" must be copied EXACTLY, character for character, from the posting. Quote the full sentence or bullet point that contains the evidence, not a single word.
- If the posting does not state a field, set value and quote to null (or use an empty list for skills). Never guess.
- role_title: only if the job title appears in the posting text.
- location: where the job is based (city/province), wherever it is stated in the posting, including inside requirement lists.
- work_mode: only if explicitly stated. "Flexible working arrangements" alone is not a work mode.
- term is the work period: a season, duration, or start and end dates (e.g. "Winter 2027", "8 months", "June 1, 2026 to August 28, 2026"). The words "internship" or "co-op" alone are not a term.
- deadline is only an application deadline, written as it appears in the posting. Never use a start date or posting date.
- Skills: include only items that would make sense in a resume's skills section: named technologies (e.g. "AWS", "React", "SQL") and specific concepts (e.g. "object-oriented programming", "CI/CD", "version control"). Exclude vague categories (e.g. "modern programming languages", "a database management system") and soft skills (e.g. "communication").
- List every named technology separately. If a platform and its services are both named (e.g. AWS, S3, Lambda), list each one.
- A skill is nice_to_have only if the posting explicitly marks it optional (e.g. "nice to have", "asset", "preferred", "bonus"). Otherwise it is required.
"""

def call_model(system: str, user: str) -> str:
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user}]}], 
        inferenceConfig={"maxTokens": 2000, "temperature": 0},
    )
    usage = response["usage"]
    print(f"[tokens in={usage['inputTokens']} out={usage['outputTokens']}, "
          f"stop={response['stopReason']}, latency={response['metrics']['latencyMs']}ms]",
          file=sys.stderr)
    if response["stopReason"]=="max_tokens": 
        raise RuntimeError("Model output was cut off (hit maxTokens)")
    return response["output"]["message"]["content"][0]["text"]

def parse_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in model output: {text[:200]}")
    return json.loads(text[start:end + 1])

SINGLE_FIELDS = ["company", "role_title", "location", "work_mode", "term", "deadline"]
LIST_FIELDS = ["required_skills", "nice_to_have_skills"]
GENERIC_TERMS = {"internship", "intern", "co-op", "coop", "internship program", "co-op program"}
WORK_MODES = {"remote", "hybrid", "onsite"}


def validate_structure(result) -> list:
    """Problems only the model can fix. Returns a list of error messages."""
    if not isinstance(result, dict):
        return ["Output is not a JSON object"]
    errors = []
    for field in SINGLE_FIELDS:
        item = result.get(field)
        if not isinstance(item, dict) or "value" not in item or "quote" not in item:
            errors.append(f'"{field}" must be an object with "value" and "quote"')
    for field in LIST_FIELDS:
        items = result.get(field)
        if not isinstance(items, list):
            errors.append(f'"{field}" must be a list')
            continue
        for i, item in enumerate(items):
            if not isinstance(item, dict) or not item.get("value") or not item.get("quote"):
                errors.append(f'"{field}[{i}]" must have a non-empty "value" and "quote"')
    return errors


def apply_rules(result: dict) -> list:
    """Rules code can enforce itself. Fixes the result and returns notes on what changed."""
    fixes = []
    term = result["term"]["value"]
    if isinstance(term, str) and term.strip().lower() in GENERIC_TERMS:
        fixes.append(f'term "{term}" is not a work period; set to null')
        result["term"] = {"value": None, "quote": None}
    mode = result["work_mode"]["value"]
    if mode is not None and (not isinstance(mode, str) or mode.lower() not in WORK_MODES):
        fixes.append(f'work_mode "{mode}" is not remote/hybrid/onsite; set to null')
        result["work_mode"] = {"value": None, "quote": None}
    return fixes

def extract(posting_text: str) -> dict:
    user = f"Job posting:\n\n{posting_text}"
    for attempt in (1, 2):
        raw = call_model(SYSTEM_PROMPT, user)
        try:
            result = parse_json(raw)
            errors = validate_structure(result)
        except ValueError as e:
            errors = [f"Invalid JSON: {e}"]
        if not errors:
            result["fixes"] = apply_rules(result)
            return result
        print(f"[attempt {attempt} invalid: {errors}]", file=sys.stderr)
        user = (f"Job posting:\n\n{posting_text}\n\n"
                f"Your previous answer had these problems: {'; '.join(errors)}. "
                "Return a corrected JSON object only.")
    raise ValueError(f"Model output still invalid after 2 attempts: {errors}")

def normalize(text: str) -> str:

    replacements = {
        "\u2018": "'", "\u2019": "'",   # curly single quotes
        "\u201c": '"', "\u201d": '"',   # curly double quotes
        "\u2013": "-", "\u2014": "-",   # en dash, em dash
        "\u00a0": " ",                  # non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def is_grounded(item: dict, posting_norm: str) -> bool:
    value = item.get("value")
    quote = item.get("quote")
    if value is None:
        return True
    if not quote:
        return False
    return normalize(quote) in posting_norm


def grounding_check(result: dict, posting_text: str) -> dict:
    checked = copy.deepcopy(result)
    posting_norm = normalize(posting_text)
    flagged = []

    for field in SINGLE_FIELDS:
        item = checked.get(field) or {"value": None, "quote": None}
        item["grounded"] = is_grounded(item, posting_norm)
        checked[field] = item
        if not item["grounded"]:
            flagged.append(field)

    for field in LIST_FIELDS:
        items = checked.get(field) or []
        for i, item in enumerate(items):
            item["grounded"] = is_grounded(item, posting_norm)
            if not item["grounded"]:
                flagged.append(f"{field}[{i}]")
        checked[field] = items

    checked["flagged"] = flagged
    return checked

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        posting = f.read()
    result = grounding_check(extract(posting), posting)
    print(json.dumps(result, indent=2))