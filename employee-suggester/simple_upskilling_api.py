#!/usr/bin/env python3
"""
Simple standalone upskilling API
"""

import json
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import the enhanced upskiller
from services.enhanced_upskiller import EnhancedUpskiller

app = FastAPI(title="Simple Upskilling API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class UpskillingRequest(BaseModel):
    resume_skills: List[str]
    job_matches: List[Dict[str, Any]]
    target_role: Optional[str] = None

@app.get("/")
def root():
    return {"status": "ok", "message": "Simple Upskilling API"}

@app.post("/upskill/enhanced")
async def generate_enhanced_upskill_plan(request: UpskillingRequest):
    """
    Generate enhanced upskilling plan based on resume analysis and job matches.
    """
    try:
        upskiller = EnhancedUpskiller()
        
        result = upskiller.generate_upskilling_plan(
            resume_skills=request.resume_skills,
            job_matches=request.job_matches,
            target_role=request.target_role
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate enhanced upskill plan: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
