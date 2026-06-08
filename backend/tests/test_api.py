"""Smoke + unit tests for the RightsAI Nigeria backend.

These run fully offline (no OpenAI key required) because the LLM service falls
back to deterministic, rule-based output when no key is configured.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.incident import DEFAULT_DISCLAIMER
from app.services import legal_mapper

client = TestClient(create_app())


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "llm_configured" in body


def test_analyze_detention() -> None:
    resp = client.post(
        "/api/analyze",
        json={
            "complaint": (
                "Police officers arrested me and detained me for two days "
                "without telling me why."
            )
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] == "Illegal Detention"
    assert "Right to Personal Liberty" in body["possible_rights"]
    assert any("Section 35" in law for law in body["relevant_laws"])
    assert body["disclaimer"] == DEFAULT_DISCLAIMER
    assert body["risk_level"] in {"Low", "Medium", "High", "Unknown"}


def test_analyze_validation_error() -> None:
    resp = client.post("/api/analyze", json={"complaint": "short"})
    assert resp.status_code == 422


def test_letter_generation() -> None:
    analyze_resp = client.post(
        "/api/analyze",
        json={"complaint": "My employer sacked me and refused to pay my salary."},
    )
    assert analyze_resp.status_code == 200
    analysis = analyze_resp.json()

    letter_resp = client.post(
        "/api/letter",
        json={
            "complaint": "My employer sacked me and refused to pay my salary.",
            "analysis": analysis,
        },
    )
    assert letter_resp.status_code == 200
    body = letter_resp.json()
    assert "Yours faithfully" in body["letter"]
    assert body["disclaimer"] == DEFAULT_DISCLAIMER


def test_legal_mapper_has_min_20_mappings() -> None:
    assert len(legal_mapper.LEGAL_MAPPINGS) >= 20


def test_legal_mapper_fallback() -> None:
    mapping = legal_mapper.get_mapping("Totally Unknown Category", "random text")
    assert mapping.category == "General Inquiry"
