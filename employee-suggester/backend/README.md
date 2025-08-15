# Backend

This package hosts the FastAPI app and ingestion logic.

## Run
```bash
uvicorn backend.app:app --reload
```

## Endpoint

**POST /ingest_resume** — multipart file field `file` (PDF/DOCX/TXT)

Returns JSON: `{ id, filename, filetype, pages, text, sections, warnings[] }`
