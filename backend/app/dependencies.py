from fastapi import Request

from app.services import ResearchService


def get_research_service(request: Request) -> ResearchService:
    return request.app.state.research_service
