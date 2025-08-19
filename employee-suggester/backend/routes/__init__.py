from .health import router as health_router
from .parse import router as parse_router
from .match import router as match_router
from .upskill import router as upskill_router
from .feedback import router as feedback_router

__all__ = [
    "health_router",
    "parse_router", 
    "match_router",
    "upskill_router",
    "feedback_router"
]
