# Build FAISS indexes for jobs and courses from data/*.jsonl
import json
import sys
from pathlib import Path

# Add the project root to Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.embed_index import build_index
DATA = ROOT / "data"
OUT = ROOT / "backend" / "models"
OUT.mkdir(parents=True, exist_ok=True)

def job_text(it: dict) -> str:
    must = ", ".join(it.get("must_have", []))
    nice = ", ".join(it.get("nice_to_have", []))
    return f"{it.get('title','')} {it.get('level','')} {it.get('location','')}. Must: {must}. Nice: {nice}. Desc: {it.get('desc','')}"

def course_text(it: dict) -> str:
    topics = ", ".join(it.get("topics", []))
    return f"{it.get('title','')}. Topics: {topics}. Level: {it.get('level','')}"

def main():
    jobs_path = DATA / "jobs" / "jobs.jsonl"
    courses_path = DATA / "courses" / "courses.jsonl"

    jobs = [json.loads(l) for l in jobs_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    courses = [json.loads(l) for l in courses_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    print("Building jobs index...")
    jp, jm = build_index(jobs, job_text, str(OUT), "jobs")
    print("Saved:", jp, jm)

    print("Building courses index...")
    cp, cm = build_index(courses, course_text, str(OUT), "courses")
    print("Saved:", cp, cm)

if __name__ == "__main__":
    main()
