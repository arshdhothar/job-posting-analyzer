import json

from extractor import extract, grounding_check

MAX_CHARS = 20000


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Body must be JSON"})

    posting = body.get("posting_text")
    if not isinstance(posting, str) or not posting.strip():
        return _response(400, {"error": 'Send JSON like {"posting_text": "..."}'})
    if len(posting) > MAX_CHARS:
        return _response(413, {"error": f"Posting too long (max {MAX_CHARS} characters)"})

    try:
        result = grounding_check(extract(posting), posting)
    except Exception as e:
        print(f"Extraction failed: {e}")
        return _response(502, {"error": "Extraction failed"})

    return _response(200, result)


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }