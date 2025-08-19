from pydantic import BaseModel, Field
from typing import List, Dict
from .common import CandidateProfile, JobProfile

class MatchRequest(BaseModel):
    candidate: CandidateProfile
    jobs: List[JobProfile]
    constraints: Dict[str, str] = {}  # e.g., {"location": "KL"}

class MatchReason(BaseModel):
    feature: str
    weight: float
    note: str

class MatchResult(BaseModel):
    job_id: str
    score: float = Field(ge=0, le=1)
    reasons: List[MatchReason]
    gaps: List[str] = []

class MatchResponse(BaseModel):
    matches: List[MatchResult]
