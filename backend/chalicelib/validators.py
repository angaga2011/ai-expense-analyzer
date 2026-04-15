from pathlib import Path

from chalicelib.utils import get_file_size_bytes


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/pdf",
}


class ValidationError(Exception):
    pass


def validate_required_fields(payload: dict, required_fields: list[str]) -> None:
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def validate_file_extension(file_name: str, allowed_extensions: set[str]) -> str:
    extension = Path(file_name).suffix.lower().lstrip(".")
    if not extension:
        raise ValidationError("File extension is missing in file_name.")
    if extension not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file extension '{extension}'. Allowed: {sorted(allowed_extensions)}"
        )
    return extension


def validate_content_type(content_type: str) -> None:
    normalized = (content_type or "").strip().lower()
    if normalized not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(
            f"Unsupported content_type '{content_type}'. Allowed: {sorted(ALLOWED_CONTENT_TYPES)}"
        )


def validate_file_size(file_bytes: bytes, max_file_size_mb: int) -> None:
    max_bytes = max_file_size_mb * 1024 * 1024
    size_bytes = get_file_size_bytes(file_bytes)
    if size_bytes > max_bytes:
        raise ValidationError(
            f"File size exceeds limit ({max_file_size_mb} MB)."
        )
