"""RightsAI Nigeria backend — FastAPI application entrypoint.

Run locally with::

    uvicorn app.main:app --reload

LEGAL NOTICE: This service provides legal INFORMATION only, never legal advice.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyze, letter
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.schemas.incident import HealthResponse
from app.services import prompt_engine

logger = logging.getLogger(__name__)

API_DESCRIPTION = (
    "AI-powered legal guidance for Nigerian citizens. "
    "**This service provides legal information only and does not provide legal "
    "advice.** Every response includes a disclaimer."
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown lifecycle: validate config and warm caches."""
    settings = get_settings()
    configure_logging(settings.log_level)

    # Startup validation.
    prompt_engine.warm_cache()
    if not settings.llm_configured:
        logger.warning(
            "Starting WITHOUT an OpenAI API key. The service will run in "
            "offline (deterministic, rule-based) mode."
        )
    else:
        logger.info("OpenAI configured with model '%s'.", settings.openai_model)

    logger.info(
        "%s v%s started in '%s' environment.",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    yield
    logger.info("%s shutting down.", settings.app_name)


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=API_DESCRIPTION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(analyze.router)
    app.include_router(letter.router)

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        """Liveness/readiness probe."""
        return HealthResponse(
            service=settings.app_name,
            version=settings.app_version,
            llm_configured=settings.llm_configured,
        )

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        """Root endpoint pointing to the docs."""
        return {
            "service": settings.app_name,
            "docs": "/docs",
            "health": "/health",
            "notice": "Legal information only. Not legal advice.",
        }

    return app


app = create_app()
