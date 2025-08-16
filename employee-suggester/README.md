# Employee Suggester (Resume → Roles & Training)

This project recommends roles and training courses from a resume.  
**This milestone** sets up repo scaffolding, seed data, and a working ingestion API that parses PDF/DOCX/TXT resumes, detects scanned PDFs, and uses OCR (if available).

## Repo Structure

```
backend/                        # FastAPI app + ingestion/parsing
data/
  resumes/                      # sample resumes (PII removed)
  jobs/                         # jobs.jsonl (one JSON per line)
  courses/                      # courses.jsonl
  taxonomy/                     # skills.csv (canonical skills + aliases)
scripts/                        # helper scripts (optional)
ui/                             # front-end (to be added later)
```

## Environment Setup

### 1) Create & activate virtualenv
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2) Install Python deps
```bash
pip install -r requirements.txt
```

### 3) System dependencies for OCR (optional but recommended)

**Tesseract OCR**
- Windows: Install Tesseract (add to PATH)
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y tesseract-ocr`

**Poppler (for pdf2image on macOS/Linux)**
- macOS: `brew install poppler`
- Ubuntu/Debian: `sudo apt-get install -y poppler-utils`
- Windows: Usually not required for this flow. If needed, install Poppler and add to PATH.

*If Tesseract isn't installed, scanned PDFs will return a warning and proceed without OCR.*

## Run the API
```bash
uvicorn backend.app:app --reload
```

## Test upload (replace with your path):
```bash
curl -F "file=@data/resumes/alex.txt" http://127.0.0.1:8000/ingest_resume
curl -F "file=@/path/to/your_resume.pdf" http://127.0.0.1:8000/ingest_resume
```

## Step 3 — Skills + Embeddings + FAISS

Build indexes (jobs & courses):
```bash
python scripts/build_indices.py
```

Run quick smoke test:
```bash
python scripts/quick_test.py
```

**What you should see:**
- A printed list of extracted skills from the sample resume.
- Top job matches re-scored with skill overlap, including which must-have skills you already have and which are missing.

## Next Milestones

- **Step 4:** Retrieval + scoring (similarity + skill overlap) + explanations  
- **Step 5:** LightGBM ranker (learning-to-rank) and evaluation (nDCG@5)

## Deploy (Render + Netlify)
- API: Render Blueprint (render.yaml). It installs deps and runs `python -m scripts.build_indices` at build, then starts Uvicorn on `$PORT`.
- Config:
  - EMBED_MODEL (default: sentence-transformers/all-MiniLM-L6-v2)
  - ALLOWED_ORIGINS (comma-separated, set to your Netlify URL for production)
- UI: Deploy `ui/` to Netlify. In the published page, set API via:
  - Click "Set API URL" → paste your Render URL (e.g., https://employee-suggester-api.onrender.com), or
  - Put it in `<meta name="api-base" content="https://…onrender.com">` and redeploy.
