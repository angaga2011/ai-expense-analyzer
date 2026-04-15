import boto3


def detect_entities(text: str, region_name: str, language_code: str = "en") -> list[dict]:
    if not text.strip():
        return []

    comprehend_client = boto3.client("comprehend", region_name=region_name)
    response = comprehend_client.detect_entities(Text=text, LanguageCode=language_code)
    entities = response.get("Entities", [])

    simplified: list[dict] = []
    for entity in entities:
        simplified.append(
            {
                "text": entity.get("Text", ""),
                "type": entity.get("Type", ""),
                "score": entity.get("Score", 0.0),
            }
        )
    return simplified


def detect_key_phrases(text: str, region_name: str, language_code: str = "en") -> list[dict]:
    if not text.strip():
        return []

    comprehend_client = boto3.client("comprehend", region_name=region_name)
    response = comprehend_client.detect_key_phrases(Text=text, LanguageCode=language_code)
    phrases = response.get("KeyPhrases", [])

    simplified: list[dict] = []
    for phrase in phrases:
        simplified.append(
            {
                "text": phrase.get("Text", ""),
                "score": phrase.get("Score", 0.0),
            }
        )
    return simplified


def analyze_text(text: str, region_name: str) -> dict:
    return {
        "entities": detect_entities(text=text, region_name=region_name),
        "key_phrases": detect_key_phrases(text=text, region_name=region_name),
    }
