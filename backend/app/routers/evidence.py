from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_research_service
from app.models import ChatRequest, ChatResponse, MeasurementList
from app.routers.common import ERROR_RESPONSES
from app.services import ResearchService


router = APIRouter(tags=["evidence"])


@router.post(
    "/api/chat",
    response_model=ChatResponse,
    responses={**ERROR_RESPONSES},
    summary="Ask an evidence-grounded question",
    description=(
        "Answers only from verified indexed excerpts. Returns NO_EVIDENCE when "
        "the catalog does not contain supporting excerpts."
    ),
)
def chat(
    request: ChatRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> ChatResponse:
    return service.chat(request)


@router.get(
    "/api/measurements",
    response_model=MeasurementList,
    responses={**ERROR_RESPONSES},
    summary="List verified measurements",
    description=(
        "Returns source-linked numeric measurements only. Empty results mean no "
        "verified matching measurements are indexed."
    ),
)
def measurements(
    service: Annotated[ResearchService, Depends(get_research_service)],
    investigation_id: str | None = None,
    variable: str | None = Query(default=None, max_length=200),
) -> MeasurementList:
    return service.measurements(investigation_id, variable)
