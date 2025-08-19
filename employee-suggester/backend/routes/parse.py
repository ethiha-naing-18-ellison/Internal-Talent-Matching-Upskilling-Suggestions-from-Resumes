from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from ..schemas.parse import ParseResumeRequest, ParseResumeResponse
from ..services.resume_parser import ResumeParser
from .health import increment_metric

router = APIRouter()

@router.post("/parse_resume", response_model=ParseResumeResponse)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse resume from uploaded file.
    """
    increment_metric("parse_calls")
    
    try:
        content = await file.read()
        parser = ResumeParser()
        profile = parser.parse_from_upload(content, file.filename)
        
        return ParseResumeResponse(profile=profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

@router.post("/parse_resume_json", response_model=ParseResumeResponse)
async def parse_resume_json(request: ParseResumeRequest):
    """
    Parse resume from raw text (for testing).
    """
    increment_metric("parse_calls")
    
    try:
        if not request.raw_text:
            raise HTTPException(status_code=400, detail="raw_text is required")
        
        parser = ResumeParser()
        profile = parser.parse_from_text(request.raw_text)
        
        return ParseResumeResponse(profile=profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
