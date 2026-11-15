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
        "Retrieves verified excerpts and returns citations linked to those excerpts. "
        "When evidence is unavailable, returns answer_status=insufficient_evidence "
        "rather than guessing. Optional scenario context uses a prior scenario analysis."
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
    summary="List verified numeric observations",
    description=(
        "Returns imported measurement rows, never staged candidates, when linked "
        "to a verified NASA source record. Pipeline-extracted values reach this "
        "store only after explicit review. Each point retains the reported value and unit, "
        "document title, URL, available page/section, and supporting excerpt. "
        "Pending candidates are never exposed. Empty data includes catalog "
        "data_availability and an explanation; no sample values are generated."
    ),
)
def measurements(
    service: Annotated[ResearchService, Depends(get_research_service)],
    investigation_id: str | None = None,
    variable: str | None = Query(default=None, max_length=200),
) -> MeasurementList:
    return service.measurements(investigation_id, variable)
