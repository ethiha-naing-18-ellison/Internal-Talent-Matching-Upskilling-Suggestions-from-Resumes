from pydantic import BaseModel
from typing import List, Dict

class PlanItem(BaseModel):
    type: str               # "course" | "microtask"
    ref_id: str             # course id or task id
    label: str
    hours: int
    prereqs: List[str] = []

class SkillPlan(BaseModel):
    skill: str
    eta_weeks: int
    items: List[PlanItem]

class UpskillRequest(BaseModel):
    target_role: str
    gaps: List[str]          # canonical skills missing or below min level

class UpskillResponse(BaseModel):
    plan: List[SkillPlan]
