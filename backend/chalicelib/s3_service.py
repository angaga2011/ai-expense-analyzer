import uuid
from datetime import datetime, timezone

import boto3

from chalicelib.utils import normalize_filename


def generate_s3_object_key(file_name: str, prefix: str = "uploads") -> str:
    normalized_name = normalize_filename(file_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}/{timestamp}-{unique_id}-{normalized_name}"


def upload_file_bytes_to_s3(
    file_bytes: bytes,
    file_name: str,
    content_type: str,
    bucket_name: str,
    region_name: str,
) -> dict:
    s3_client = boto3.client("s3", region_name=region_name)
    object_key = generate_s3_object_key(file_name)

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=file_bytes,
        ContentType=content_type,
    )

    return {
        "bucket": bucket_name,
        "key": object_key,
        "s3_uri": f"s3://{bucket_name}/{object_key}",
    }
