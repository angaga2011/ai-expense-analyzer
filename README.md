# AI Expense Analyzer

Upload a receipt, invoice, or transaction screenshot. The backend stores the file in S3, extracts text with Textract, analyzes it with Comprehend, and returns a structured JSON summary. A lightweight HTML/JS frontend lets you interact with it directly in the browser.

## Project Structure

```text
frontend/
  index.html
  styles.css
  scripts.js

backend/
  app.py
  requirements.txt
  .env.example
  chalicelib/
    __init__.py
    config.py
    utils.py
    validators.py
    response_builder.py
    s3_service.py
    textract_service.py
    comprehend_service.py
    parser.py
```

## Environment Variables

Copy values from `backend/.env.example` into your local environment before running:

- `AWS_REGION` (default: `us-east-1`)
- `S3_BUCKET_NAME` (required)
- `MAX_FILE_SIZE_MB` (default: `5`)
- `ALLOWED_EXTENSIONS` (default: `jpg,jpeg,png,pdf`)

## Install and Run

### Backend

```bash
cd backend
pip install -r requirements.txt
chalice local
```

Default local URL: `http://127.0.0.1:8000`

### Frontend

No install needed — open `frontend/index.html` directly in your browser:

```bash
# from the project root
open frontend/index.html        # macOS
xdg-open frontend/index.html   # Linux
start frontend/index.html      # Windows
```

Make sure the backend is running before using the frontend.

## API Endpoints

### GET `/health`

Simple service check.

### POST `/analyze`

Request body (JSON):

```json
{
  "file_name": "receipt1.jpg",
  "content_type": "image/jpeg",
  "file_base64": "BASE64_ENCODED_FILE_BYTES"
}
```

Successful response example:

```json
{
  "success": true,
  "message": "Document analyzed successfully.",
  "data": {
    "document_type": "receipt",
    "amount": "42.50",
    "date": "2026-04-12",
    "entity": "Coffee Shop",
    "summary": "Receipt from Coffee Shop for 42.50 on 2026-04-12.",
    "raw_text_preview": "COFFEE SHOP ... TOTAL 42.50 ..."
  }
}
```

Error response example:

```json
{
  "success": false,
  "message": "Missing required fields: file_base64"
}
```

## Notes

- This is a student-friendly starter and intentionally keeps parsing rule-based and lightweight.
- AWS credentials/permissions are required for S3, Textract, and Comprehend.
- Typical IAM permissions needed: `s3:PutObject`, `textract:DetectDocumentText`, and Comprehend detect actions.
