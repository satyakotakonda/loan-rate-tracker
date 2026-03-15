import json
import logging
from datetime import datetime, timezone

from google import genai
from google.genai import types

from app.config import settings
from app.models.loan_rate import AgentQuery, AgentResponse, BankRate

logger = logging.getLogger(__name__)

_AGENT_PROMPT = """You are a financial data expert specializing in Indian bank loan rates.
The user will ask a natural language question about loan interest rates.
Answer using your knowledge of current (or most recently available) loan rates from Indian banks.

IMPORTANT:
- Return ONLY a valid JSON object — no markdown, no extra text, no code fences.
- Your response must strictly follow this JSON schema:
{{
  "summary": "<string: a brief summary answering the user's question>",
  "banks": [
    {{
      "bank_name": "<string>",
      "interest_rate_min": <number>,
      "interest_rate_max": <number>,
      "processing_fee": "<string>",
      "loan_type": "<string: home, personal, car, education, or business>"
    }}
  ],
  "advice": "<string: actionable tips or eligibility notes>"
}}

User question: {query}
"""


def _build_agent_response(query: str, raw_json: dict) -> AgentResponse:
    """Parse the LLM JSON output into an AgentResponse."""
    banks = [
        BankRate(
            bank_name=b.get("bank_name", ""),
            interest_rate_min=float(b.get("interest_rate_min", 0)),
            interest_rate_max=float(b.get("interest_rate_max", 0)),
            processing_fee=b.get("processing_fee"),
            loan_type=b.get("loan_type", ""),
        )
        for b in raw_json.get("banks", [])
    ]
    return AgentResponse.build(
        query=query,
        summary=raw_json.get("summary", ""),
        banks=banks,
        advice=raw_json.get("advice"),
        timestamp=datetime.now(timezone.utc),
    )


def query_agent(request: AgentQuery) -> AgentResponse:
    """
    Send a natural language loan rate query to Gemini AI and return a
    structured AgentResponse.  Falls back to OpenAI if Gemini is not
    configured.
    """
    prompt = _AGENT_PROMPT.format(query=request.query)

    if settings.GEMINI_API_KEY:
        return _query_gemini(request.query, prompt)

    if settings.OPENAI_API_KEY:
        return _query_openai(request.query, prompt)

    raise RuntimeError(
        "No LLM API key configured. Set GEMINI_API_KEY or OPENAI_API_KEY."
    )


def _query_gemini(query: str, prompt: str) -> AgentResponse:
    """Call Google Gemini and parse the structured JSON response."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    raw_text = response.text.strip()
    logger.info("Gemini response received (%d chars)", len(raw_text))

    try:
        raw_json = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini returned invalid JSON: {exc}. Raw response: {raw_text[:500]}") from exc
    return _build_agent_response(query, raw_json)


def _query_openai(query: str, prompt: str) -> AgentResponse:
    """Call OpenAI as a fallback and parse the structured JSON response."""
    from openai import OpenAI  # imported lazily — optional dependency

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw_text = (completion.choices[0].message.content or "").strip()
    logger.info("OpenAI response received (%d chars)", len(raw_text))

    try:
        raw_json = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"OpenAI returned invalid JSON: {exc}. Raw response: {raw_text[:500]}") from exc
    return _build_agent_response(query, raw_json)

