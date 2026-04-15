import base64
import re
from pathlib import Path


def decode_base64_file(file_base64: str) -> bytes:
    try:
        return base64.b64decode(file_base64, validate=True)
    except Exception as error:  # pragma: no cover - broad to normalize error message
        raise ValueError("Invalid base64-encoded file content.") from error


def truncate_preview(text: str, max_length: int = 280) -> str:
    clean_text = (text or "").strip()
    if len(clean_text) <= max_length:
        return clean_text
    return f"{clean_text[: max_length - 3]}..."


def normalize_filename(file_name: str) -> str:
    base_name = Path(file_name).name.strip().replace(" ", "_")
    normalized = re.sub(r"[^A-Za-z0-9._-]", "", base_name)
    return normalized or "uploaded_file"


def get_file_size_bytes(file_bytes: bytes) -> int:
    return len(file_bytes)


def file_size_mb(file_bytes: bytes) -> float:
    return get_file_size_bytes(file_bytes) / (1024 * 1024)
