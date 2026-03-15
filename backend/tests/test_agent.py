"""Tests for the LLM agent endpoint and supporting functions."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.loan_rate import AgentQuery, AgentResponse, BankRate
from app.services.llm_extractor import _build_agent_response, query_agent

client = TestClient(app)


# ---------------------------------------------------------------------------
# _build_agent_response tests
# ---------------------------------------------------------------------------

def test_build_agent_response_full():
    """_build_agent_response correctly maps a complete JSON payload."""
    raw = {
        "summary": "SBI has the lowest home loan rate.",
        "banks": [
            {
                "bank_name": "SBI",
                "interest_rate_min": 8.5,
                "interest_rate_max": 9.2,
                "processing_fee": "0.35%",
                "loan_type": "home",
            }
        ],
        "advice": "Compare processing fees.",
    }
    resp = _build_agent_response("lowest home loan?", raw)
    assert isinstance(resp, AgentResponse)
    assert resp.query == "lowest home loan?"
    assert resp.response["summary"] == "SBI has the lowest home loan rate."
    assert resp.response["advice"] == "Compare processing fees."
    banks = resp.response["banks"]
    assert len(banks) == 1
    assert banks[0]["bank_name"] == "SBI"
    assert banks[0]["interest_rate_min"] == 8.5


def test_build_agent_response_missing_banks():
    """_build_agent_response handles missing 'banks' key gracefully."""
    raw = {"summary": "No data", "advice": ""}
    resp = _build_agent_response("query", raw)
    assert resp.response["banks"] == []


def test_build_agent_response_partial_bank():
    """_build_agent_response tolerates missing fields within a bank entry."""
    raw = {
        "summary": "Partial data",
        "banks": [{"bank_name": "HDFC"}],
        "advice": None,
    }
    resp = _build_agent_response("query", raw)
    bank = resp.response["banks"][0]
    assert bank["bank_name"] == "HDFC"
    assert bank["interest_rate_min"] == 0.0


# ---------------------------------------------------------------------------
# query_agent tests
# ---------------------------------------------------------------------------

def test_query_agent_raises_when_no_keys(monkeypatch):
    """query_agent raises RuntimeError when neither API key is configured."""
    monkeypatch.setattr("app.services.llm_extractor.settings.GEMINI_API_KEY", "")
    monkeypatch.setattr("app.services.llm_extractor.settings.OPENAI_API_KEY", "")
    with pytest.raises(RuntimeError, match="No LLM API key configured"):
        query_agent(AgentQuery(query="test"))


def test_query_agent_uses_gemini_when_key_set(monkeypatch):
    """query_agent delegates to _query_gemini when GEMINI_API_KEY is set."""
    monkeypatch.setattr("app.services.llm_extractor.settings.GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr("app.services.llm_extractor.settings.OPENAI_API_KEY", "")

    fake_response = AgentResponse(
        query="test",
        response={"summary": "ok", "banks": [], "advice": ""},
        timestamp=datetime.now(timezone.utc),
    )
    with patch("app.services.llm_extractor._query_gemini", return_value=fake_response) as mock_gemini:
        result = query_agent(AgentQuery(query="test"))
    mock_gemini.assert_called_once()
    assert result is fake_response


def test_query_agent_falls_back_to_openai(monkeypatch):
    """query_agent falls back to OpenAI when GEMINI_API_KEY is not set."""
    monkeypatch.setattr("app.services.llm_extractor.settings.GEMINI_API_KEY", "")
    monkeypatch.setattr("app.services.llm_extractor.settings.OPENAI_API_KEY", "fake-openai-key")

    fake_response = AgentResponse(
        query="test",
        response={"summary": "ok", "banks": [], "advice": ""},
        timestamp=datetime.now(timezone.utc),
    )
    with patch("app.services.llm_extractor._query_openai", return_value=fake_response) as mock_openai:
        result = query_agent(AgentQuery(query="test"))
    mock_openai.assert_called_once()
    assert result is fake_response


# ---------------------------------------------------------------------------
# POST /api/v1/agent/query endpoint tests
# ---------------------------------------------------------------------------

def _fake_agent_response(request: AgentQuery) -> AgentResponse:
    return AgentResponse(
        query=request.query,
        response={
            "summary": "Test summary",
            "banks": [
                {
                    "bank_name": "Test Bank",
                    "interest_rate_min": 7.5,
                    "interest_rate_max": 9.0,
                    "processing_fee": "1%",
                    "loan_type": "home",
                }
            ],
            "advice": "Test advice",
        },
        timestamp=datetime.now(timezone.utc),
    )


def test_agent_query_endpoint_success():
    """POST /api/v1/agent/query returns 200 with a valid response when the agent succeeds."""
    with patch("app.api.routes.query_agent", side_effect=_fake_agent_response):
        resp = client.post("/api/v1/agent/query", json={"query": "best home loan?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "best home loan?"
    assert data["response"]["summary"] == "Test summary"
    assert len(data["response"]["banks"]) == 1


def test_agent_query_endpoint_no_keys():
    """POST /api/v1/agent/query returns 503 when no API keys are configured."""
    with patch("app.api.routes.query_agent", side_effect=RuntimeError("No LLM API key configured")):
        resp = client.post("/api/v1/agent/query", json={"query": "test"})
    assert resp.status_code == 503
    assert "No LLM API key configured" in resp.json()["detail"]


def test_agent_query_endpoint_unexpected_error():
    """POST /api/v1/agent/query returns 500 on unexpected errors."""
    with patch("app.api.routes.query_agent", side_effect=ValueError("unexpected")):
        resp = client.post("/api/v1/agent/query", json={"query": "test"})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Agent query failed"


def test_agent_query_endpoint_missing_body():
    """POST /api/v1/agent/query returns 422 for invalid request bodies."""
    resp = client.post("/api/v1/agent/query", json={})
    assert resp.status_code == 422
