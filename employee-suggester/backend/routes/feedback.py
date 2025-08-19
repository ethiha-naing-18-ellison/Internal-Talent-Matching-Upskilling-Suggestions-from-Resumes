from fastapi import APIRouter, HTTPException
from ..schemas.feedback import FeedbackRequest, FeedbackResponse
from ..services.audit import AuditLogger
from .health import increment_metric

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on a recommendation.
    """
    increment_metric("feedback_calls")
    
    try:
        logger = AuditLogger()
        logger.log_feedback(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            action=request.action,
            reason=request.reason
        )
        
        return FeedbackResponse(status="ok")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")
