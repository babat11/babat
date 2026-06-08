"""LLM service: async OpenAI integration for analysis and letter generation.

Responsibilities:
    * Build prompts via the prompt engine.
    * Call the OpenAI API asynchronously with JSON-output enforcement for
      analysis.
    * Validate and normalise model output into Pydantic models.
    * Degrade gracefully (deterministic offline mode) when no API key is
      configured, so the service remains runnable and testable without secrets.

This module never raises raw provider errors to callers; it wraps them in
:class:`LLMServiceError`.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.schemas.incident import (
    DEFAULT_DISCLAIMER,
    AnalysisResponse,
    LetterResponse,
)
from app.services import legal_mapper, prompt_engine

logger = logging.getLogger(__name__)

_ANALYSIS_KEYS = (
    "category",
    "summary_facts",
    "possible_rights",
    "relevant_laws",
    "evidence_to_collect",
    "recommended_actions",
    "agencies",
    "risk_level",
    "disclaimer",
)


class LLMServiceError(RuntimeError):
    """Raised when the LLM service cannot produce a valid response."""


class LLMService:
    """Thin async wrapper around the OpenAI Chat Completions API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: Any | None = None
        if self._settings.llm_configured:
            self._client = self._build_client()
        else:
            logger.warning(
                "OPENAI_API_KEY not set; LLMService running in offline "
                "(deterministic) mode. Responses are rule-based only."
            )

    def _build_client(self) -> Any:
        """Construct an AsyncOpenAI client (imported lazily)."""
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise LLMServiceError(
                "The 'openai' package is required but not installed."
            ) from exc

        return AsyncOpenAI(
            api_key=self._settings.openai_api_key,
            timeout=self._settings.openai_timeout_seconds,
            max_retries=self._settings.openai_max_retries,
        )

    @property
    def is_offline(self) -> bool:
        """Whether the service is running without a configured LLM."""
        return self._client is None

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    async def analyze_incident(self, complaint: str) -> AnalysisResponse:
        """Analyze a complaint and return a structured, enriched response.

        Args:
            complaint: The user's complaint text.

        Returns:
            A validated :class:`AnalysisResponse`.

        Raises:
            LLMServiceError: If the model output cannot be parsed.
        """
        if self.is_offline:
            raw = self._offline_analysis(complaint)
        else:
            prompt = prompt_engine.get_analyze_prompt(complaint)
            content = await self._chat(
                prompt=prompt,
                json_mode=True,
                system="You return only valid JSON. No prose, no code fences.",
            )
            raw = self._parse_json(content)

        normalised = self._normalise_analysis(raw)
        enriched = legal_mapper.enrich_analysis(normalised, complaint)
        enriched["disclaimer"] = DEFAULT_DISCLAIMER
        try:
            return AnalysisResponse.model_validate(enriched)
        except Exception as exc:  # noqa: BLE001 - surface as service error
            raise LLMServiceError(f"Invalid analysis structure: {exc}") from exc

    async def generate_letter(
        self, complaint: str, analysis: AnalysisResponse
    ) -> LetterResponse:
        """Generate a formal complaint letter from a complaint + analysis.

        Args:
            complaint: The original complaint text.
            analysis: The structured analysis.

        Returns:
            A :class:`LetterResponse`.
        """
        analysis_json = json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2)

        if self.is_offline:
            letter = self._offline_letter(complaint, analysis)
        else:
            prompt = prompt_engine.get_letter_prompt(complaint, analysis_json)
            letter = await self._chat(
                prompt=prompt,
                json_mode=False,
                system=(
                    "You draft cautious, professional complaint letters. "
                    "Return plain text only."
                ),
            )
            letter = letter.strip()

        return LetterResponse(letter=letter, disclaimer=DEFAULT_DISCLAIMER)

    # ------------------------------------------------------------------ #
    # OpenAI call
    # ------------------------------------------------------------------ #
    async def _chat(self, prompt: str, json_mode: bool, system: str) -> str:
        """Issue a single chat completion request."""
        if self._client is None:  # pragma: no cover - guarded by callers
            raise LLMServiceError("LLM client is not configured.")

        kwargs: dict[str, Any] = {
            "model": self._settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:  # noqa: BLE001 - wrap provider errors
            logger.exception("OpenAI request failed")
            raise LLMServiceError(f"LLM request failed: {exc}") from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMServiceError("LLM returned an empty response.")
        return content

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        """Parse model JSON output, tolerating stray code fences."""
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            # Drop an optional leading language hint like "json".
            if "\n" in text:
                first, rest = text.split("\n", 1)
                if first.strip().lower() in {"json", ""}:
                    text = rest
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMServiceError(f"LLM did not return valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise LLMServiceError("LLM JSON output was not an object.")
        return data

    @staticmethod
    def _normalise_analysis(raw: dict[str, Any]) -> dict[str, Any]:
        """Ensure all expected keys exist with sane types/defaults."""
        out: dict[str, Any] = {}
        list_keys = {
            "summary_facts",
            "possible_rights",
            "relevant_laws",
            "evidence_to_collect",
            "recommended_actions",
            "agencies",
        }
        for key in _ANALYSIS_KEYS:
            value = raw.get(key)
            if key in list_keys:
                out[key] = legal_mapper._as_str_list(value)
            elif key == "risk_level":
                out[key] = str(value) if value else "Unknown"
            else:
                out[key] = str(value) if value is not None else ""
        return out

    # ------------------------------------------------------------------ #
    # Offline deterministic fallbacks (no API key required)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _offline_analysis(complaint: str) -> dict[str, Any]:
        """Produce a deterministic, rule-based analysis without an LLM."""
        mapping = legal_mapper.get_mapping(None, complaint)
        return {
            "category": mapping.category,
            "summary_facts": [
                "Complaint received and processed in offline mode.",
                "Automated keyword-based classification applied.",
            ],
            "possible_rights": list(mapping.rights),
            "relevant_laws": list(mapping.constitution) + list(mapping.laws),
            "evidence_to_collect": [
                "Any written records or correspondence",
                "Names and contact details of witnesses",
                "Photographs, videos, or other media if available",
                "A written timeline of events",
            ],
            "recommended_actions": [
                "Document the timeline of events in detail",
                "Preserve any available evidence",
                "Consider contacting a relevant agency listed below",
                "Consider consulting a qualified legal practitioner",
            ],
            "agencies": list(mapping.agencies),
            "risk_level": mapping.risk_level,
            "disclaimer": DEFAULT_DISCLAIMER,
        }

    @staticmethod
    def _offline_letter(complaint: str, analysis: AnalysisResponse) -> str:
        """Produce a deterministic complaint letter without an LLM."""
        rights = ", ".join(analysis.possible_rights) or "relevant rights"
        laws = ", ".join(analysis.relevant_laws) or "applicable laws"
        agency = analysis.agencies[0] if analysis.agencies else "[Recipient/Agency Name]"
        evidence = "; ".join(analysis.evidence_to_collect) or "available evidence"
        return (
            "[Your Full Name]\n"
            "[Your Address]\n"
            "[Date]\n\n"
            f"The Director\n{agency}\n[Recipient Address]\n\n"
            f"Dear Sir/Madam,\n\n"
            f"RE: REQUEST FOR REVIEW OF A POTENTIAL {analysis.category.upper()} "
            "MATTER\n\n"
            "I write to respectfully bring the following matter to your "
            "attention and to request a review.\n\n"
            f"Summary of the matter: {complaint.strip()}\n\n"
            f"This situation may potentially involve {rights}, and could be "
            f"relevant to provisions such as {laws}. I make no legal "
            "conclusions and request only that the matter be reviewed.\n\n"
            f"I have sought to preserve the following evidence where possible: "
            f"{evidence}.\n\n"
            "I would be grateful if this matter could be investigated and any "
            "appropriate steps taken. Please let me know if further "
            "information is required.\n\n"
            "Yours faithfully,\n\n"
            "____________________\n"
            "[Your Full Name]\n"
            "[Your Phone Number]\n"
            "[Your Email]\n\n"
            "Note: This letter is provided as legal information, not legal "
            "advice."
        )


_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Return a process-wide :class:`LLMService` singleton."""
    global _service
    if _service is None:
        _service = LLMService()
    return _service
