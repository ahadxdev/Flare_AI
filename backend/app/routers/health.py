from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_research_service
from app.errors import APIError
from app.models import ErrorResponse, HealthResponse
from app.services import ResearchService


router = APIRouter(tags=["health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Check API health",
    description="Returns a simple health status for the FLARE AI API.",
)
def health() -> HealthResponse:
    return HealthResponse()


@router.get(
    "/api/ready", response_model=HealthResponse,
    responses={503: {"model": ErrorResponse, "description": "Local catalog is unavailable or empty."}},
    summary="Check local catalog readiness",
    description="Checks local database access and a non-empty catalog without contacting external services.",
)
def ready(service: Annotated[ResearchService, Depends(get_research_service)]) -> HealthResponse:
    try:
        catalog = service.list_investigations(None, None, None, None, 1, 1)
        if catalog.total:
            return HealthResponse()
    except Exception:
        pass
    raise APIError(503, "INTERNAL_ERROR", "The local research catalog is not ready.")
