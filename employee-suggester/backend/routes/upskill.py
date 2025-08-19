from fastapi import APIRouter, HTTPException
from ..schemas.upskill import UpskillRequest, UpskillResponse
from ..services.recommender import UpskillRecommender
from .health import increment_metric

router = APIRouter()

@router.post("/upskill", response_model=UpskillResponse)
async def generate_upskill_plan(request: UpskillRequest):
    """
    Generate upskilling plan for skill gaps.
    """
    increment_metric("upskill_calls")
    
    try:
        recommender = UpskillRecommender()
        result = recommender.build_upskill_plan(request.gaps, request.target_role)
        
        return UpskillResponse(plan=result['plan'])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate upskill plan: {str(e)}")
