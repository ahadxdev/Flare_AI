from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_research_service
from app.models import (
    ComparisonRequest,
    ComparisonResponse,
    ScenarioAnalysisResponse,
    ScenarioRequest,
)
from app.routers.common import ERROR_RESPONSES
from app.services import ResearchService


router = APIRouter(tags=["analysis"])


@router.post(
    "/api/scenarios/analyze",
    response_model=ScenarioAnalysisResponse,
    responses={**ERROR_RESPONSES},
    summary="Analyze scenario research relevance",
    description=(
        "Ranks indexed investigations by transparent research relevance. "
        "The score is not a fire-risk score or probability; user-entered conditions "
        "remain hypothetical."
    ),
)
def analyze_scenario(
    scenario: ScenarioRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> ScenarioAnalysisResponse:
    return service.analyze_scenario(scenario)


@router.post(
    "/api/compare",
    response_model=ComparisonResponse,
    responses={**ERROR_RESPONSES},
    summary="Compare investigations",
    description=(
        "Compares at least two distinct indexed investigations field by field. "
        "Raw values and units are preserved; incomplete fields and incompatible "
        "pressure units are marked not comparable rather than converted or inferred."
    ),
)
def compare(
    request: ComparisonRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> ComparisonResponse:
    return service.compare(request)
