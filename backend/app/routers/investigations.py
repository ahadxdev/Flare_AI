from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_research_service
from app.errors import APIError
from app.models import (
    DataAvailability,
    Environment,
    Investigation,
    InvestigationPage,
    ResearchArea,
)
from app.routers.common import ERROR_RESPONSES
from app.services import ResearchService


router = APIRouter(prefix="/api/investigations", tags=["investigations"])


@router.get(
    "",
    response_model=InvestigationPage,
    responses={**ERROR_RESPONSES},
    summary="Search investigations",
    description=(
        "Searches and filters the locally indexed canonical investigation catalog. "
        "Only imported source-backed records are returned."
    ),
)
def list_investigations(
    service: Annotated[ResearchService, Depends(get_research_service)],
    q: str | None = Query(default=None, max_length=250),
    research_area: ResearchArea | None = None,
    environment: Environment | None = None,
    data_availability: DataAvailability | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> InvestigationPage:
    return service.list_investigations(
        q, research_area, environment, data_availability, page, page_size
    )


@router.get(
    "/{investigation_id}",
    response_model=Investigation,
    responses={**ERROR_RESPONSES},
    summary="Get an investigation",
    description="Returns one canonical investigation, including its source provenance.",
)
def get_investigation(
    investigation_id: str,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> Investigation:
    item = service.get_investigation(investigation_id)
    if item is None:
        raise APIError(404, "NOT_FOUND", "Investigation not found.")
    return item
