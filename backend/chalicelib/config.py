import os
from dataclasses import dataclass


def _parse_allowed_extensions(raw_value: str) -> set[str]:
    values = [item.strip().lower().lstrip(".") for item in raw_value.split(",")]
    return {item for item in values if item}


def _parse_max_file_size_mb(raw_value: str, default_value: int) -> int:
    try:
        parsed = int(raw_value)
        return parsed if parsed > 0 else default_value
    except (TypeError, ValueError):
        return default_value


@dataclass(frozen=True)
class Settings:
    aws_region: str
    s3_bucket_name: str
    max_file_size_mb: int
    allowed_extensions: set[str]


def load_settings() -> Settings:
    default_region = "us-east-1"
    default_max_file_size_mb = 5
    default_extensions = "jpg,jpeg,png,pdf"

    aws_region = os.getenv("AWS_REGION", default_region)
    s3_bucket_name = os.getenv("S3_BUCKET_NAME", "").strip()
    max_file_size_mb = _parse_max_file_size_mb(
        os.getenv("MAX_FILE_SIZE_MB", str(default_max_file_size_mb)),
        default_max_file_size_mb,
    )
    allowed_extensions = _parse_allowed_extensions(
        os.getenv("ALLOWED_EXTENSIONS", default_extensions)
    )

    return Settings(
        aws_region=aws_region,
        s3_bucket_name=s3_bucket_name,
        max_file_size_mb=max_file_size_mb,
        allowed_extensions=allowed_extensions,
    )
