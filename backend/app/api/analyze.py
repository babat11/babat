"""``/api/analyze`` route: analyze a complaint into structured legal info."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.incident import AnalysisResponse, IncidentRequest
from app.services.llm_service import LLMService, LLMServiceError, get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze a complaint into structured legal information",
    response_description="Structured legal information (not legal advice).",
)
async def analyze(
    payload: IncidentRequest,
    service: LLMService = Depends(get_llm_service),
) -> AnalysisResponse:
    """Analyze a citizen complaint and return structured legal information.

    This endpoint returns legal INFORMATION only and never legal advice. Every
    response includes a disclaimer.
    """
    logger.info("Received analyze request (offline=%s)", service.is_offline)
    try:
        return await service.analyze_incident(payload.complaint)
    except LLMServiceError as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The analysis service is temporarily unavailable.",
        ) from exc
