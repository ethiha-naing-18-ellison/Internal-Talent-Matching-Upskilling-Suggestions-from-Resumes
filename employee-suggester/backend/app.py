from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from .ingest import parse_resume_file

app = FastAPI(title="Employee Suggester — Ingestion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Employee Suggester API (ingestion ready)"}

@app.post("/ingest_resume")
async def ingest_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = parse_resume_file(content, file.filename)
        result["id"] = str(uuid4())
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

# --- Minimal suggestion endpoints (no persistence, pass text directly) ---
from .skills import SkillTaxonomy
from .retriever import search, score_with_skills
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "backend" / "models"
TAXO_CSV = ROOT / "data" / "taxonomy" / "skills.csv"

def _extract_skills(text: str):
    tax = SkillTaxonomy(str(TAXO_CSV))
    return tax.normalize(text or "")

@app.get("/suggest/roles")
def suggest_roles_api(
    resume_text: str = Query(..., description="Paste resume text here"),
    topk: int = Query(5, ge=1, le=20)
):
    skills = _extract_skills(resume_text)
    jobs_idx = str(MODELS_DIR / "jobs.index")
    jobs_meta = str(MODELS_DIR / "jobs.meta.jsonl")

    hits = search(jobs_idx, jobs_meta, resume_text, topk=20)
    rescored = []
    for r in hits:
        s = score_with_skills(skills, r, r["score"])
        j = r["raw"]
        must = j.get("must_have", [])
        have = [sk for sk in skills if sk in must]
        miss = [sk for sk in must if sk not in skills]
        rescored.append({
            "job_id": j.get("id"),
            "title": j.get("title"),
            "score": round(float(s), 4),
            "matched_skills": have,
            "missing_skills": miss
        })
    rescored.sort(key=lambda x: x["score"], reverse=True)
    return {"roles": rescored[:topk]}
