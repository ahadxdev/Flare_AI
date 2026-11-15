from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_research_service
from app.models import ReportRequest, ReportResponse
from app.routers.common import ERROR_RESPONSES
from app.services import ResearchService


router = APIRouter(tags=["reports"])


@router.post(
    "/api/reports",
    response_model=ReportResponse,
    responses={**ERROR_RESPONSES},
    summary="Generate an evidence brief",
    description=(
        "Builds an HTML or Markdown evidence brief from an existing scenario "
        "analysis, selected investigations, verified measurements, and indexed "
        "source evidence."
    ),
)
def create_report(
    request: ReportRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> ReportResponse:
    return service.create_report(request)
