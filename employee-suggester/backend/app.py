import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from .ingest import parse_resume_file

# Import new modular routes
from .routes import health_router, parse_router, match_router, upskill_router, feedback_router

app = FastAPI(title="Employee Suggester — Internal Talent Matching & Upskilling")

allowed = os.getenv("ALLOWED_ORIGINS", "*")
origins = ["*"] if allowed.strip() == "*" else [o.strip() for o in allowed.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)

# Include new modular routes
app.include_router(health_router)
app.include_router(parse_router)
app.include_router(match_router)
app.include_router(upskill_router)
app.include_router(feedback_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Employee Suggester API (Internal Talent Matching & Upskilling)"}

# Keep existing endpoints for backward compatibility
@app.get("/healthz")
def health():
    return {"status": "ok"}

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

@app.get("/suggest/roles/v2")
def suggest_roles_enhanced_api(
    resume_text: str = Query(..., description="Paste resume text here"),
    topk: int = Query(5, ge=1, le=20)
):
    """
    Enhanced role suggestion using v1.3.0.0 matching logic.
    Includes skills, projects, and education analysis.
    """
    from .services.resume_parser import ResumeParser
    from .services.matcher import Matcher
    from .schemas.common import CandidateProfile, Skill, JobProfile, JobSkillReq
    
    # Parse resume to get structured data
    parser = ResumeParser()
    parsed_data = parser.parse_resume_text(resume_text)
    
    # Extract skills
    skills = _extract_skills(resume_text)
    
    # Create candidate profile
    candidate_skills = [Skill(name=skill, canonical=skill, level=2) for skill in skills]
    candidate = CandidateProfile(
        skills=candidate_skills,
        projects=parsed_data.get('projects', []),
        education=parsed_data.get('education', []),
        roles=parsed_data.get('roles', []),
        certs=parsed_data.get('certs', []),
        location=parsed_data.get('location'),
        dept=parsed_data.get('dept')
    )
    
    # Get job candidates
    jobs_idx = str(MODELS_DIR / "jobs.index")
    jobs_meta = str(MODELS_DIR / "jobs.meta.jsonl")
    hits = search(jobs_idx, jobs_meta, resume_text, topk=20)
    
    # Use enhanced matcher
    matcher = Matcher()
    rescored = []
    
    for r in hits:
        j = r["raw"]
        
        # Convert job data to JobProfile
        required_skills = [JobSkillReq(skill=skill, min_level=1) for skill in j.get("must_have", [])]
        job_profile = JobProfile(
            id=j.get("id", ""),
            title=j.get("title", ""),
            dept=j.get("dept"),
            location=j.get("location"),
            required=required_skills,
            nice=j.get("nice_to_have", [])
        )
        
        # Score using enhanced matcher
        result = matcher.score_candidate_to_job(candidate, job_profile)
        
        # Extract matched and missing skills for backward compatibility
        have = [skill.name for skill in candidate_skills if skill.name in j.get("must_have", [])]
        miss = [skill for skill in j.get("must_have", []) if skill not in [s.name for s in candidate_skills]]
        
        rescored.append({
            "job_id": j.get("id"),
            "title": j.get("title"),
            "score": result['score'],
            "matched_skills": have,
            "missing_skills": miss,
            "enhanced_reasons": [reason.dict() for reason in result['reasons']]
        })
    
    rescored.sort(key=lambda x: x["score"], reverse=True)
    return {"roles": rescored[:topk], "version": "1.3.0.0"}
