import logging
from datetime import datetime, timezone
from typing import Optional

from cachetools import TTLCache

from app.config import settings
from app.models.loan_rate import AgentQuery, AgentResponse, BestRatesResponse, LoanRate, RatesResponse
from app.services.llm_extractor import query_agent

logger = logging.getLogger(__name__)

_cache: TTLCache = TTLCache(maxsize=settings.CACHE_MAXSIZE, ttl=settings.CACHE_TTL)


class RateAggregator:
    """Aggregates loan rates via the LLM agent with TTL caching."""

    CACHE_KEY_ALL = "all_rates"

    def get_all_rates(self, force_refresh: bool = False) -> RatesResponse:
        """
        Get all loan rates via the LLM agent (cached).

        A single agent query retrieves both personal and home loan rates to
        minimise LLM API calls.
        """
        if not force_refresh and self.CACHE_KEY_ALL in _cache:
            logger.info("Returning cached loan rates")
            return _cache[self.CACHE_KEY_ALL]

        logger.info("Fetching fresh loan rates via LLM agent")
        all_rates: list[LoanRate] = []
        try:
            agent_resp: AgentResponse = query_agent(
                AgentQuery(
                    query=(
                        "List all major Indian banks with both personal loan and home loan "
                        "interest rates, including processing fees"
                    )
                )
            )
            for bank in agent_resp.response.get("banks", []):
                rate_min = float(bank.get("interest_rate_min", 0))
                rate_max = float(bank.get("interest_rate_max", 0))
                if rate_min <= 0:
                    logger.warning(
                        "Skipping %s — missing interest_rate_min from agent response",
                        bank.get("bank_name", "unknown"),
                    )
                    continue
                all_rates.append(
                    LoanRate(
                        bank_name=bank.get("bank_name", ""),
                        loan_type=bank.get("loan_type", "personal"),
                        interest_rate_min=rate_min,
                        interest_rate_max=rate_max,
                        processing_fee=bank.get("processing_fee"),
                        last_updated=datetime.now(timezone.utc),
                    )
                )
            logger.info("Fetched %d rates total via LLM agent", len(all_rates))
        except Exception as e:
            logger.error("Error fetching bank rates via agent: %s", e)

        response = RatesResponse(
            data=all_rates,
            total=len(all_rates),
            last_refreshed=datetime.now(timezone.utc),
        )
        _cache[self.CACHE_KEY_ALL] = response
        return response

    def get_personal_loan_rates(self) -> RatesResponse:
        """Get all personal loan rates."""
        all_resp = self.get_all_rates()
        personal = [r for r in all_resp.data if r.loan_type == "personal"]
        personal_sorted = sorted(personal, key=lambda x: x.interest_rate_min)
        return RatesResponse(
            data=personal_sorted,
            total=len(personal_sorted),
            last_refreshed=all_resp.last_refreshed,
        )

    def get_home_loan_rates(self) -> RatesResponse:
        """Get all home loan rates."""
        all_resp = self.get_all_rates()
        home = [r for r in all_resp.data if r.loan_type == "home"]
        home_sorted = sorted(home, key=lambda x: x.interest_rate_min)
        return RatesResponse(
            data=home_sorted,
            total=len(home_sorted),
            last_refreshed=all_resp.last_refreshed,
        )

    def get_rates_by_bank(self, bank_name: str) -> RatesResponse:
        """Get all rates for a specific bank (case-insensitive partial match)."""
        all_resp = self.get_all_rates()
        bank_rates = [
            r for r in all_resp.data
            if bank_name.lower() in r.bank_name.lower()
        ]
        return RatesResponse(
            data=bank_rates,
            total=len(bank_rates),
            last_refreshed=all_resp.last_refreshed,
        )

    def get_filtered_rates(
        self,
        loan_type: Optional[str] = None,
        bank_name: Optional[str] = None,
        sort_by: Optional[str] = "interest_rate_min",
        order: str = "asc",
    ) -> RatesResponse:
        """Get rates with optional filtering and sorting."""
        all_resp = self.get_all_rates()
        rates = list(all_resp.data)

        if loan_type:
            rates = [r for r in rates if r.loan_type == loan_type.lower()]

        if bank_name:
            rates = [r for r in rates if bank_name.lower() in r.bank_name.lower()]

        if sort_by in ("interest_rate_min", "interest_rate_max", "bank_name"):
            reverse = order.lower() == "desc"
            rates = sorted(rates, key=lambda r: getattr(r, sort_by), reverse=reverse)

        return RatesResponse(
            data=rates,
            total=len(rates),
            last_refreshed=all_resp.last_refreshed,
        )

    def get_best_rates(self) -> BestRatesResponse:
        """Get best (lowest minimum rate) rates for each loan type."""
        personal_resp = self.get_personal_loan_rates()
        home_resp = self.get_home_loan_rates()

        return BestRatesResponse(
            best_personal_loan=personal_resp.data[0] if personal_resp.data else None,
            best_home_loan=home_resp.data[0] if home_resp.data else None,
            personal_loans_sorted=personal_resp.data,
            home_loans_sorted=home_resp.data,
        )


rate_aggregator = RateAggregator()
