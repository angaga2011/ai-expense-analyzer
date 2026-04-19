import boto3

_MAX_COMPREHEND_BYTES = 4_900


def _truncate_for_comprehend(text: str) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= _MAX_COMPREHEND_BYTES:
        return text
    return encoded[:_MAX_COMPREHEND_BYTES].decode("utf-8", errors="ignore")


def analyze_text(text: str, region_name: str) -> dict:
    if not text.strip():
        return {"entities": []}

    safe_text = _truncate_for_comprehend(text)
    comprehend_client = boto3.client("comprehend", region_name=region_name)
    response = comprehend_client.detect_entities(Text=safe_text, LanguageCode="en")

    entities: list[dict] = []
    for entity in response.get("Entities", []):
        entities.append(
            {
                "text": entity.get("Text", ""),
                "type": entity.get("Type", ""),
                "score": entity.get("Score", 0.0),
            }
        )

    return {"entities": entities}
