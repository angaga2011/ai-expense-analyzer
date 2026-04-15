from chalice import Chalice, BadRequestError, Response

from chalicelib.comprehend_service import analyze_text
from chalicelib.config import load_settings
from chalicelib.parser import parse_document_data
from chalicelib.response_builder import build_error_response, build_success_response
from chalicelib.s3_service import upload_file_bytes_to_s3
from chalicelib.textract_service import combine_text_lines, detect_document_text_from_s3, extract_text_lines
from chalicelib.utils import decode_base64_file
from chalicelib.validators import (
    ValidationError,
    validate_content_type,
    validate_file_extension,
    validate_file_size,
    validate_required_fields,
)

app = Chalice(app_name="ai-expense-analyzer-backend")


def _json_response(body: dict, status_code: int) -> Response:
    return Response(body=body, status_code=status_code, headers={"Content-Type": "application/json"})


@app.route("/health", methods=["GET"], cors=True)
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "ai-expense-analyzer-backend",
    }


@app.route("/analyze", methods=["POST"], cors=True)
def analyze_document() -> Response:
    settings = load_settings()

    try:
        if not settings.s3_bucket_name:
            return _json_response(
                build_error_response("Missing required environment variable: S3_BUCKET_NAME."),
                status_code=500,
            )

        request = app.current_request
        payload = request.json_body
        if payload is None:
            raise BadRequestError("Request must contain a JSON body.")

        validate_required_fields(payload, ["file_name", "file_base64", "content_type"])

        file_name = payload["file_name"]
        file_base64 = payload["file_base64"]
        content_type = payload["content_type"]

        validate_file_extension(file_name, settings.allowed_extensions)
        validate_content_type(content_type)

        file_bytes = decode_base64_file(file_base64)
        validate_file_size(file_bytes, settings.max_file_size_mb)

        upload_result = upload_file_bytes_to_s3(
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type,
            bucket_name=settings.s3_bucket_name,
            region_name=settings.aws_region,
        )

        textract_response = detect_document_text_from_s3(
            bucket_name=upload_result["bucket"],
            object_key=upload_result["key"],
            region_name=settings.aws_region,
        )
        text_lines = extract_text_lines(textract_response)
        extracted_text = combine_text_lines(text_lines)

        if not extracted_text.strip():
            return _json_response(
                build_error_response("No text could be extracted from this document."),
                status_code=422,
            )

        comprehend_result = analyze_text(text=extracted_text, region_name=settings.aws_region)
        parsed_data = parse_document_data(extracted_text, comprehend_result)

        return _json_response(build_success_response(parsed_data), status_code=200)

    except ValidationError as error:
        return _json_response(build_error_response(str(error)), status_code=400)
    except BadRequestError as error:
        return _json_response(build_error_response(str(error)), status_code=400)
    except Exception as error:  # pragma: no cover - final fallback for API safety
        app.log.error("Unexpected /analyze error: %s", error, exc_info=True)
        return _json_response(
            build_error_response("Internal server error during document analysis."),
            status_code=500,
        )
