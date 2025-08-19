from fastapi import APIRouter, HTTPException
from ..schemas.match import MatchRequest, MatchResponse, MatchResult
from ..services.matcher import Matcher
from .health import increment_metric

router = APIRouter()

@router.post("/match", response_model=MatchResponse)
async def match_candidate(request: MatchRequest):
    """
    Match a candidate against a list of jobs.
    """
    increment_metric("match_calls")
    
    try:
        matcher = Matcher()
        matches = []
        
        for job in request.jobs:
            # Convert job dict to JobProfile if needed
            if isinstance(job, dict):
                from ..schemas.common import JobProfile, JobSkillReq
                job_skill_reqs = [JobSkillReq(**req) for req in job.get('required', [])]
                job_profile = JobProfile(
                    id=job['id'],
                    title=job['title'],
                    dept=job.get('dept'),
                    location=job.get('location'),
                    required=job_skill_reqs,
                    nice=job.get('nice', [])
                )
            else:
                job_profile = job
            
            # Score candidate against job
            result = matcher.score_candidate_to_job(request.candidate, job_profile)
            
            # Create match result
            match_result = MatchResult(
                job_id=job_profile.id,
                score=result['score'],
                reasons=result['reasons'],
                gaps=result['gaps']
            )
            
            matches.append(match_result)
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return MatchResponse(matches=matches)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match candidate: {str(e)}")
