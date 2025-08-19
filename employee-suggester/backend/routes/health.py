from fastapi import APIRouter
from typing import Dict, Any
import json
from pathlib import Path

router = APIRouter()

# Simple metrics counter
_metrics = {
    "total_requests": 0,
    "parse_calls": 0,
    "match_calls": 0,
    "upskill_calls": 0,
    "feedback_calls": 0
}

@router.get("/healthz")
def healthz():
    """Health check endpoint."""
    return {"status": "ok"}

@router.get("/metrics")
def metrics():
    """Get application metrics."""
    return _metrics

@router.get("/jobs")
def get_jobs():
    """Get sample jobs for frontend testing."""
    try:
        jobs_file = Path(__file__).resolve().parents[2] / "data" / "jobs" / "jobs.jsonl"
        jobs = []
        with open(jobs_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    jobs.append(json.loads(line))
        return jobs
    except Exception as e:
        print(f"Error loading jobs: {e}")
        # Return sample jobs if file not found
        return [
            {"id": "J1", "title": "Data Engineer", "dept": "IT", "location": "KL", "required": [{"skill": "python", "min_level": 3}], "nice": ["docker", "sql"]},
            {"id": "J2", "title": "Backend Developer", "dept": "IT", "location": "JB", "required": [{"skill": "nodejs", "min_level": 3}], "nice": ["aws", "docker"]}
        ]

def increment_metric(metric_name: str):
    """Increment a metric counter."""
    if metric_name in _metrics:
        _metrics[metric_name] += 1
    _metrics["total_requests"] += 1
