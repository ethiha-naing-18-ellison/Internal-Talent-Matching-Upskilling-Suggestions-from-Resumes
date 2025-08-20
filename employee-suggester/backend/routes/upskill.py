from fastapi import APIRouter, HTTPException
from ..schemas.upskill import UpskillRequest, UpskillResponse
from ..services.enhanced_upskiller import EnhancedUpskiller
from .health import increment_metric

router = APIRouter()

@router.post("/upskill", response_model=UpskillResponse)
async def generate_upskill_plan(request: UpskillRequest):
    """
    Generate upskilling plan for skill gaps.
    """
    increment_metric("upskill_calls")
    
    try:
        upskiller = EnhancedUpskiller()
        result = upskiller.generate_upskilling_plan(
            resume_skills=request.gaps,
            job_matches=[],
            target_role=request.target_role
        )
        
        return UpskillResponse(plan=result['plan'])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate upskill plan: {str(e)}")

@router.post("/upskill/enhanced")
async def generate_enhanced_upskill_plan(request: dict):
    """
    Generate enhanced upskilling plan based on resume analysis and job matches.
    
    Expected request format:
    {
        "resume_skills": ["python", "sql", "react"],
        "job_matches": [
            {
                "title": "Data Scientist",
                "score": 0.75,
                "missing_skills": ["machine learning", "aws"]
            }
        ],
        "target_role": "Data Scientist"  # optional
    }
    """
    increment_metric("enhanced_upskill_calls")
    
    try:
        upskiller = EnhancedUpskiller()
        
        resume_skills = request.get("resume_skills", [])
        job_matches = request.get("job_matches", [])
        target_role = request.get("target_role")
        
        result = upskiller.generate_upskilling_plan(
            resume_skills=resume_skills,
            job_matches=job_matches,
            target_role=target_role
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate enhanced upskill plan: {str(e)}")

@router.get("/upskill/skills/{skill_name}")
async def get_skill_details(skill_name: str):
    """
    Get detailed information about a specific skill.
    """
    try:
        upskiller = EnhancedUpskiller()
        skill_details = upskiller.get_skill_details(skill_name.lower())
        
        if not skill_details:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        
        return skill_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skill details: {str(e)}")

@router.get("/upskill/roles/{role_name}")
async def get_role_details(role_name: str):
    """
    Get detailed information about a specific job role.
    """
    try:
        upskiller = EnhancedUpskiller()
        role_details = upskiller.get_job_category_details(role_name)
        
        if not role_details:
            raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
        
        return role_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get role details: {str(e)}")
