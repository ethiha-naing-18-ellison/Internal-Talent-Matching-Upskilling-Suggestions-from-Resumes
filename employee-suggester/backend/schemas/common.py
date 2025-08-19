from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

class Skill(BaseModel):
    name: str
    canonical: str
    level: int = Field(ge=0, le=5)
    last_used: Optional[str] = None  # "YYYY-MM" or None

class Role(BaseModel):
    title: str
    start: Optional[str] = None      # "YYYY-MM"
    end: Optional[str] = None

class CandidateProfile(BaseModel):
    candidate_id: Optional[str] = None
    name: Optional[str] = None       # avoid storing full legal name elsewhere
    phone: Optional[str] = None      # phone number
    email: Optional[str] = None      # email address
    dept: Optional[str] = None
    location: Optional[str] = None
    seniority: Optional[str] = None
    skills: List[Skill] = []
    roles: List[Role] = []
    certs: List[str] = []
    education: List[str] = []
    projects: List[str] = []
    rewards: List[str] = []

class JobSkillReq(BaseModel):
    skill: str
    min_level: int

class JobProfile(BaseModel):
    id: str
    title: str
    dept: Optional[str] = None
    location: Optional[str] = None
    required: List[JobSkillReq] = []
    nice: List[str] = []
