from app.routers.analysis import router as analysis_router
from app.routers.evidence import router as evidence_router
from app.routers.health import router as health_router
from app.routers.investigations import router as investigations_router
from app.routers.reports import router as reports_router

__all__ = [
    "analysis_router",
    "evidence_router",
    "health_router",
    "investigations_router",
    "reports_router",
]
