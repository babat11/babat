"""Pydantic models for the RightsAI Nigeria legal guidance API.

These schemas define the request/response contracts for the analyze and
letter endpoints. All models use Pydantic v2.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["Low", "Medium", "High", "Unknown"]

DEFAULT_DISCLAIMER = (
    "This is legal information and not legal advice. RightsAI Nigeria does not "
    "create a lawyer-client relationship. For advice specific to your "
    "situation, please consult a qualified legal practitioner."
)


class IncidentRequest(BaseModel):
    """Incoming complaint submitted by a user for analysis."""

    complaint: str = Field(
        ...,
        min_length=10,
        max_length=10_000,
        description="Free-text description of the incident from the user.",
        examples=[
            "Police officers arrested me and detained me for two days without "
            "telling me why."
        ],
    )


class AnalysisResponse(BaseModel):
    """Structured legal-information analysis of a complaint.

    Language is intentionally cautious: this is legal information, not advice.
    """

    category: str = Field(
        default="",
        description="Best-effort classification of the incident type.",
    )
    summary_facts: list[str] = Field(
        default_factory=list,
        description="Neutral facts extracted from the complaint.",
    )
    possible_rights: list[str] = Field(
        default_factory=list,
        description="Rights that may potentially be relevant.",
    )
    relevant_laws: list[str] = Field(
        default_factory=list,
        description="Laws/sections that could be relevant for context.",
    )
    evidence_to_collect: list[str] = Field(
        default_factory=list,
        description="Evidence the user may wish to preserve.",
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="General, non-prescriptive next steps to consider.",
    )
    agencies: list[str] = Field(
        default_factory=list,
        description="Agencies/organisations that may be relevant to contact.",
    )
    risk_level: RiskLevel = Field(
        default="Unknown",
        description="Cautious indication of urgency/severity.",
    )
    disclaimer: str = Field(
        default=DEFAULT_DISCLAIMER,
        description="Legal disclaimer included in every response.",
    )


class LetterRequest(BaseModel):
    """Request to generate a formal complaint letter."""

    complaint: str = Field(
        ...,
        min_length=10,
        max_length=10_000,
        description="The original complaint text.",
    )
    analysis: AnalysisResponse = Field(
        ...,
        description="The structured analysis produced by /api/analyze.",
    )


class LetterResponse(BaseModel):
    """Generated formal complaint letter."""

    letter: str = Field(
        ...,
        description="The generated complaint letter text.",
    )
    disclaimer: str = Field(
        default=DEFAULT_DISCLAIMER,
        description="Legal disclaimer included in every response.",
    )


class HealthResponse(BaseModel):
    """Health-check payload."""

    status: Literal["ok"] = "ok"
    service: str = "rightsai-nigeria-backend"
    version: str = "0.1.0"
    llm_configured: bool = False
