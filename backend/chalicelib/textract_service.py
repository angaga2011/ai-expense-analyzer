import boto3


def detect_document_text_from_s3(
    bucket_name: str,
    object_key: str,
    region_name: str,
) -> dict:
    textract_client = boto3.client("textract", region_name=region_name)
    return textract_client.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": object_key,
            }
        }
    )


def extract_text_lines(textract_response: dict) -> list[str]:
    lines: list[str] = []
    for block in textract_response.get("Blocks", []):
        if block.get("BlockType") == "LINE" and block.get("Text"):
            lines.append(block["Text"].strip())
    return lines


def combine_text_lines(text_lines: list[str]) -> str:
    return "\n".join(line for line in text_lines if line)
