from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    candidate_id: str
    job_id: str
    action: str           # "shortlist" | "reject" | "hire"
    reason: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
