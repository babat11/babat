"""``/api/letter`` route: generate a formal complaint letter."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.incident import LetterRequest, LetterResponse
from app.services.llm_service import LLMService, LLMServiceError, get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["letter"])


@router.post(
    "/letter",
    response_model=LetterResponse,
    summary="Generate a formal complaint letter",
    response_description="A formal complaint letter (legal information only).",
)
async def letter(
    payload: LetterRequest,
    service: LLMService = Depends(get_llm_service),
) -> LetterResponse:
    """Generate a formal complaint letter from a complaint and its analysis."""
    logger.info("Received letter request (offline=%s)", service.is_offline)
    try:
        return await service.generate_letter(payload.complaint, payload.analysis)
    except LLMServiceError as exc:
        logger.error("Letter generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The letter service is temporarily unavailable.",
        ) from exc
