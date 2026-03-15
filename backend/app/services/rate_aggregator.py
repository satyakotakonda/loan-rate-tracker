import logging
from datetime import datetime
from typing import Optional

from cachetools import TTLCache

from app.config import settings
from app.models.loan_rate import BestRatesResponse, LoanRate, RatesResponse
from app.scrapers.axis_scraper import AxisScraper
from app.scrapers.bob_scraper import BoBScraper
from app.scrapers.canara_scraper import CanaraScaper
from app.scrapers.hdfc_scraper import HDFCScraper
from app.scrapers.icici_scraper import ICICIScraper
from app.scrapers.kotak_scraper import KotakScraper
from app.scrapers.pnb_scraper import PNBScraper
from app.scrapers.sbi_scraper import SBIScraper

logger = logging.getLogger(__name__)

_cache: TTLCache = TTLCache(maxsize=settings.CACHE_MAXSIZE, ttl=settings.CACHE_TTL)


def _get_all_scrapers():
    return [
        SBIScraper(),
        HDFCScraper(),
        ICICIScraper(),
        AxisScraper(),
        PNBScraper(),
        KotakScraper(),
        BoBScraper(),
        CanaraScaper(),
    ]


class RateAggregator:
    """Aggregates loan rates from all bank scrapers with TTL caching."""

    CACHE_KEY_ALL = "all_rates"

    def get_all_rates(self, force_refresh: bool = False) -> RatesResponse:
        """Get all loan rates from all banks (cached)."""
        if not force_refresh and self.CACHE_KEY_ALL in _cache:
            logger.info("Returning cached loan rates")
            return _cache[self.CACHE_KEY_ALL]

        logger.info("Fetching fresh loan rates from all banks")
        all_rates: list[LoanRate] = []
        for scraper in _get_all_scrapers():
            try:
                rates = scraper.get_all_rates()
                all_rates.extend(rates)
                logger.info(f"Fetched {len(rates)} rates from {scraper.bank_name}")
            except Exception as e:
                logger.error(f"Error with scraper {scraper.bank_name}: {e}")

        response = RatesResponse(
            data=all_rates,
            total=len(all_rates),
            last_refreshed=datetime.utcnow(),
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
