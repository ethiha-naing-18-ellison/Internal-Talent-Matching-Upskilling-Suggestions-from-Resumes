import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.io import append_jsonl, get_config_path
from ..utils.embeddings import hash_text

class AuditLogger:
    """Log system activities and user feedback."""
    
    def __init__(self):
        self.audit_dir = Path(__file__).resolve().parents[2] / ".audit"
        self.audit_dir.mkdir(exist_ok=True)
        
        self.recs_file = self.audit_dir / "recs.jsonl"
        self.feedback_file = self.audit_dir / "feedback.jsonl"
    
    def log_recommendation(self, request_id: str, candidate_stub: str, job_id: str, 
                          score: float, reasons: list, model_version: str = "1.0"):
        """Log a recommendation for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "candidate_hash": hash_text(candidate_stub),
            "job_id": job_id,
            "score": score,
            "reasons": [{"feature": r.feature, "weight": r.weight, "note": r.note} for r in reasons],
            "model_version": model_version
        }
        
        append_jsonl(log_entry, str(self.recs_file))
    
    def log_feedback(self, candidate_id: str, job_id: str, action: str, 
                    reason: Optional[str] = None):
        """Log user feedback on recommendations."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "candidate_id": hash_text(candidate_id),  # Hash for privacy
            "job_id": job_id,
            "action": action,
            "reason": reason
        }
        
        append_jsonl(log_entry, str(self.feedback_file))
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get statistics from feedback logs."""
        try:
            feedback_data = []
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        feedback_data.append(json.loads(line))
            
            # Calculate statistics
            total_feedback = len(feedback_data)
            action_counts = {}
            
            for entry in feedback_data:
                action = entry.get('action', 'unknown')
                action_counts[action] = action_counts.get(action, 0) + 1
            
            return {
                "total_feedback": total_feedback,
                "action_counts": action_counts,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error reading feedback stats: {e}")
            return {
                "total_feedback": 0,
                "action_counts": {},
                "last_updated": datetime.now().isoformat()
            }
