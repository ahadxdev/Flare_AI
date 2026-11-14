import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings
from app.chat_provider import OpenAICompatibleChatProvider
from app.errors import APIError
from app.logging_config import configure_logging
from app.models import ErrorResponse
from app.routers import (
    analysis_router,
    evidence_router,
    health_router,
    investigations_router,
    reports_router,
)
from app.services import ResearchService, SQLiteResearchService
from app.store import SQLiteStore


logger = logging.getLogger("flare.api")


def create_app(
    database_path: str | None = None,
    settings: Settings | None = None,
    research_service: ResearchService | None = None,
) -> FastAPI:
    config = settings or Settings.from_env()
    configure_logging(config.log_level)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        logger.info("FLARE AI API started")
        yield
        logger.info("FLARE AI API stopped")

    app = FastAPI(
        title="FLARE AI API",
        version="1.0.0",
        description=(
            "Evidence-first NASA PSI investigation discovery and research relevance "
            "analysis. Relevance is not fire risk; missing evidence is never inferred."
        ),
        lifespan=lifespan,
    )
    if research_service is None:
        chat_provider = None
        if config.llm_api_key and config.llm_model:
            chat_provider = OpenAICompatibleChatProvider(
                api_key=config.llm_api_key,
                model=config.llm_model,
                base_url=config.llm_base_url,
                timeout_seconds=config.llm_timeout_seconds,
            )
        research_service = SQLiteResearchService(
            SQLiteStore(database_path or config.database_path),
            chat_provider=chat_provider,
        )
    app.state.research_service = research_service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_origins),
        allow_methods=list(config.cors_methods),
        allow_headers=list(config.cors_headers),
        allow_credentials=config.cors_allow_credentials,
    )

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        logger.info(
            "HTTP request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response

    @app.exception_handler(APIError)
    async def handle_api_error(_: Request, exc: APIError) -> JSONResponse:
        body = ErrorResponse.model_validate(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        body = ErrorResponse.model_validate(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "The request did not match the expected format.",
                    "details": [
                        {
                            "field": ".".join(str(part) for part in error["loc"]),
                            "message": error["msg"],
                        }
                        for error in exc.errors()
                    ],
                }
            }
        )
        return JSONResponse(status_code=422, content=body.model_dump(mode="json"))

    @app.exception_handler(HTTPException)
    async def handle_http_error(_: Request, exc: HTTPException) -> JSONResponse:
        code = "NOT_FOUND" if exc.status_code == 404 else "VALIDATION_ERROR"
        body = ErrorResponse.model_validate(
            {
                "error": {
                    "code": code,
                    "message": str(exc.detail),
                    "details": [],
                }
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(mode="json"),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API error", exc_info=exc)
        body = ErrorResponse.model_validate(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected server error occurred.",
                    "details": [],
                }
            }
        )
        return JSONResponse(status_code=500, content=body.model_dump(mode="json"))

    app.include_router(health_router)
    app.include_router(investigations_router)
    app.include_router(analysis_router)
    app.include_router(evidence_router)
    app.include_router(reports_router)
    return app


app = create_app()
