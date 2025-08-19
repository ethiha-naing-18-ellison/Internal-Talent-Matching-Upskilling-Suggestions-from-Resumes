from pydantic import BaseModel
from typing import Optional
from .common import CandidateProfile

class ParseResumeRequest(BaseModel):
    # Either upload via multipart in route OR pass a pre-extracted text for testing
    raw_text: Optional[str] = None

class ParseResumeResponse(BaseModel):
    profile: CandidateProfile
