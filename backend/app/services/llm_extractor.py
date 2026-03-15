import json
import logging
from datetime import datetime

import httpx
from openai import OpenAI

from app.config import settings
from app.models.loan_rate import LoanRate

logger = logging.getLogger(__name__)

# Module-level client; instantiated lazily so the missing API key at import
# time does not raise an error (the key may be set via env at startup).
_openai_client: OpenAI | None = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

BANK_CONFIGS: dict[str, dict] = {
    "sbi": {
        "bank_name": "State Bank of India",
        "bank_logo_url": "https://www.sbi.co.in/favicon.ico",
        "personal_loan_url": "https://www.sbi.co.in/web/personal-banking/loans/personal-loan",
        "home_loan_url": "https://www.sbi.co.in/web/personal-banking/loans/home-loans/sbi-home-loan",
        "fallback": {
            "personal": {
                "interest_rate_min": 11.15,
                "interest_rate_max": 15.30,
                "processing_fee": "1.50% of loan amount (min ₹1,000, max ₹15,000) + GST",
                "loan_amount_min": 25000,
                "loan_amount_max": 2000000,
                "tenure_min": 6,
                "tenure_max": 72,
                "rate_type": "floating",
            },
            "home": {
                "interest_rate_min": 8.50,
                "interest_rate_max": 10.15,
                "processing_fee": "0.35% of loan amount (min ₹2,000, max ₹10,000) + GST",
                "loan_amount_min": 1000000,
                "loan_amount_max": 100000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
    "hdfc": {
        "bank_name": "HDFC Bank",
        "bank_logo_url": "https://www.hdfcbank.com/favicon.ico",
        "personal_loan_url": "https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan",
        "home_loan_url": "https://www.hdfcbank.com/personal/borrow/popular-loans/home-loan",
        "fallback": {
            "personal": {
                "interest_rate_min": 10.50,
                "interest_rate_max": 21.00,
                "processing_fee": "Up to 2.50% of loan amount + GST",
                "loan_amount_min": 50000,
                "loan_amount_max": 4000000,
                "tenure_min": 12,
                "tenure_max": 60,
                "rate_type": "fixed",
            },
            "home": {
                "interest_rate_min": 8.70,
                "interest_rate_max": 9.85,
                "processing_fee": "Up to 0.50% of loan amount or ₹3,000 (whichever is higher) + GST",
                "loan_amount_min": 300000,
                "loan_amount_max": 100000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
    "icici": {
        "bank_name": "ICICI Bank",
        "bank_logo_url": "https://www.icicibank.com/favicon.ico",
        "personal_loan_url": "https://www.icicibank.com/personal-banking/loans/personal-loan",
        "home_loan_url": "https://www.icicibank.com/personal-banking/loans/home-loan",
        "fallback": {
            "personal": {
                "interest_rate_min": 10.65,
                "interest_rate_max": 16.00,
                "processing_fee": "Up to 2.50% of loan amount + GST",
                "loan_amount_min": 50000,
                "loan_amount_max": 5000000,
                "tenure_min": 12,
                "tenure_max": 72,
                "rate_type": "fixed",
            },
            "home": {
                "interest_rate_min": 8.75,
                "interest_rate_max": 9.80,
                "processing_fee": "0.50% - 2.00% of loan amount + GST",
                "loan_amount_min": 500000,
                "loan_amount_max": 500000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
    "axis": {
        "bank_name": "Axis Bank",
        "bank_logo_url": "https://www.axisbank.com/favicon.ico",
        "personal_loan_url": "https://www.axisbank.com/retail/loans/personal-loan",
        "home_loan_url": "https://www.axisbank.com/retail/loans/home-loan",
        "fallback": {
            "personal": {
                "interest_rate_min": 10.49,
                "interest_rate_max": 22.00,
                "processing_fee": "Up to 2% of loan amount + GST",
                "loan_amount_min": 50000,
                "loan_amount_max": 4000000,
                "tenure_min": 12,
                "tenure_max": 60,
                "rate_type": "fixed",
            },
            "home": {
                "interest_rate_min": 8.75,
                "interest_rate_max": 13.30,
                "processing_fee": "1% of loan amount + GST (min ₹10,000)",
                "loan_amount_min": 300000,
                "loan_amount_max": 500000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
    "pnb": {
        "bank_name": "Punjab National Bank",
        "bank_logo_url": "https://www.pnbindia.in/favicon.ico",
        "personal_loan_url": "https://www.pnbindia.in/personal-loan.html",
        "home_loan_url": "https://www.pnbindia.in/home-loan.html",
        "fallback": {
            "personal": {
                "interest_rate_min": 11.40,
                "interest_rate_max": 16.95,
                "processing_fee": "1% of loan amount + GST (min ₹1,000, max ₹15,000)",
                "loan_amount_min": 25000,
                "loan_amount_max": 2000000,
                "tenure_min": 6,
                "tenure_max": 72,
                "rate_type": "floating",
            },
            "home": {
                "interest_rate_min": 8.50,
                "interest_rate_max": 10.25,
                "processing_fee": "0.35% of loan amount + GST (max ₹15,000)",
                "loan_amount_min": 500000,
                "loan_amount_max": 100000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
    "kotak": {
        "bank_name": "Kotak Mahindra Bank",
        "bank_logo_url": "https://www.kotak.com/favicon.ico",
        "personal_loan_url": "https://www.kotak.com/en/personal-banking/loans/personal-loan.html",
        "home_loan_url": "https://www.kotak.com/en/personal-banking/loans/home-loan.html",
        "fallback": {
            "personal": {
                "interest_rate_min": 10.99,
                "interest_rate_max": 24.00,
                "processing_fee": "Up to 3% of loan amount + GST",
                "loan_amount_min": 50000,
                "loan_amount_max": 4000000,
                "tenure_min": 12,
                "tenure_max": 60,
                "rate_type": "fixed",
            },
            "home": {
                "interest_rate_min": 8.75,
                "interest_rate_max": 9.60,
                "processing_fee": "0.50% - 1.00% of loan amount + GST",
                "loan_amount_min": 500000,
                "loan_amount_max": 100000000,
                "tenure_min": 12,
                "tenure_max": 240,
                "rate_type": "floating",
            },
        },
    },
    "bob": {
        "bank_name": "Bank of Baroda",
        "bank_logo_url": "https://www.bankofbaroda.in/favicon.ico",
        "personal_loan_url": "https://www.bankofbaroda.in/personal-banking/loans/personal-loan",
        "home_loan_url": "https://www.bankofbaroda.in/personal-banking/loans/home-loan",
        "fallback": {
            "personal": {
                "interest_rate_min": 11.05,
                "interest_rate_max": 18.75,
                "processing_fee": "2% of loan amount + GST (min ₹1,000, max ₹10,000)",
                "loan_amount_min": 50000,
                "loan_amount_max": 1500000,
                "tenure_min": 12,
                "tenure_max": 60,
                "rate_type": "floating",
            },
            "home": {
                "interest_rate_min": 8.40,
                "interest_rate_max": 10.65,
                "processing_fee": "0.25% - 0.50% of loan amount + GST",
                "loan_amount_min": 500000,
                "loan_amount_max": 200000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
    "canara": {
        "bank_name": "Canara Bank",
        "bank_logo_url": "https://canarabank.com/favicon.ico",
        "personal_loan_url": "https://canarabank.com/User_page.aspx?othermenu=91&menuid=9&submenu=4",
        "home_loan_url": "https://canarabank.com/User_page.aspx?othermenu=91&menuid=9&submenu=2",
        "fallback": {
            "personal": {
                "interest_rate_min": 11.10,
                "interest_rate_max": 16.20,
                "processing_fee": "0.50% of loan amount + GST (min ₹1,000, max ₹5,000)",
                "loan_amount_min": 25000,
                "loan_amount_max": 1000000,
                "tenure_min": 12,
                "tenure_max": 60,
                "rate_type": "floating",
            },
            "home": {
                "interest_rate_min": 8.40,
                "interest_rate_max": 11.25,
                "processing_fee": "0.25% of loan amount + GST (min ₹1,500, max ₹10,000)",
                "loan_amount_min": 500000,
                "loan_amount_max": 100000000,
                "tenure_min": 12,
                "tenure_max": 360,
                "rate_type": "floating",
            },
        },
    },
}

_LLM_PROMPT_TEMPLATE = """You are a financial data extraction assistant.
Extract loan rate information from the following bank webpage HTML and return a JSON object.

Bank: {bank_name}
Loan Type: {loan_type}

Return ONLY a valid JSON object with these fields (use null if a value cannot be found):
{{
  "interest_rate_min": <float, minimum interest rate in % per annum>,
  "interest_rate_max": <float, maximum interest rate in % per annum>,
  "processing_fee": <string, description of processing fee>,
  "loan_amount_min": <integer, minimum loan amount in INR>,
  "loan_amount_max": <integer, maximum loan amount in INR>,
  "tenure_min": <integer, minimum tenure in months>,
  "tenure_max": <integer, maximum tenure in months>,
  "rate_type": <string, "fixed" or "floating">
}}

HTML content (may be truncated):
{html}
"""


def fetch_page(url: str) -> str | None:
    """Fetch HTML content from the given URL using configured headers and timeout."""
    try:
        with httpx.Client(
            headers=settings.DEFAULT_HEADERS,
            timeout=settings.REQUEST_TIMEOUT,
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch page {url}: {e}")
        return None


def extract_rates_with_llm(
    html: str,
    bank_config: dict,
    loan_type: str,
) -> dict | None:
    """Send page HTML to the OpenAI LLM and return extracted rate data as a dict."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set; skipping LLM extraction")
        return None

    try:
        client = _get_openai_client()
        # Truncate HTML to ~12,000 chars to stay within typical LLM context
        # limits while keeping costs predictable (roughly 3,000 tokens).
        prompt = _LLM_PROMPT_TEMPLATE.format(
            bank_name=bank_config["bank_name"],
            loan_type=loan_type,
            html=html[:12000],
        )
        completion = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = completion.choices[0].message.content or ""
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw)
        return extracted
    except Exception as e:
        logger.warning(f"LLM extraction failed for {bank_config['bank_name']} {loan_type}: {e}")
        return None


def _build_loan_rate(
    bank_config: dict,
    loan_type: str,
    data: dict,
    source_url: str,
) -> LoanRate:
    """Build a LoanRate model from extracted or fallback data."""
    return LoanRate(
        bank_name=bank_config["bank_name"],
        bank_logo_url=bank_config["bank_logo_url"],
        loan_type=loan_type,
        interest_rate_min=float(data["interest_rate_min"]),
        interest_rate_max=float(data["interest_rate_max"]),
        processing_fee=str(data["processing_fee"]),
        loan_amount_min=int(data["loan_amount_min"]),
        loan_amount_max=int(data["loan_amount_max"]),
        tenure_min=int(data["tenure_min"]),
        tenure_max=int(data["tenure_max"]),
        source_url=source_url,
        rate_type=str(data["rate_type"]),
        last_updated=datetime.utcnow(),
    )


def get_bank_rates(bank_key: str) -> list[LoanRate]:
    """
    Fetch personal and home loan rates for a single bank.

    Attempts LLM extraction from the live page; falls back to hardcoded
    defaults if the page cannot be fetched or LLM extraction fails.
    """
    bank_config = BANK_CONFIGS[bank_key]
    rates: list[LoanRate] = []

    for loan_type in ("personal", "home"):
        url_key = f"{loan_type}_loan_url"
        source_url = bank_config[url_key]
        fallback = bank_config["fallback"][loan_type]

        data = None
        html = fetch_page(source_url)
        if html:
            data = extract_rates_with_llm(html, bank_config, loan_type)

        if data is None:
            logger.info(
                f"Using fallback data for {bank_config['bank_name']} {loan_type} loan"
            )
            data = fallback

        try:
            rates.append(_build_loan_rate(bank_config, loan_type, data, source_url))
        except Exception as e:
            logger.error(
                f"Failed to build LoanRate for {bank_config['bank_name']} {loan_type}: {e}"
            )
            rates.append(_build_loan_rate(bank_config, loan_type, fallback, source_url))

    return rates


def get_all_bank_rates() -> list[LoanRate]:
    """Fetch rates for all configured banks and return a combined list."""
    all_rates: list[LoanRate] = []
    for bank_key in BANK_CONFIGS:
        try:
            rates = get_bank_rates(bank_key)
            all_rates.extend(rates)
            logger.info(f"Fetched {len(rates)} rates for {BANK_CONFIGS[bank_key]['bank_name']}")
        except Exception as e:
            logger.error(f"Error fetching rates for bank '{bank_key}': {e}")
    return all_rates
