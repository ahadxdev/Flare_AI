from fastapi import APIRouter

from app.models import HealthResponse


router = APIRouter(tags=["health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Check API health",
    description="Returns a simple health status for the FLARE AI API.",
)
def health() -> HealthResponse:
    return HealthResponse()
