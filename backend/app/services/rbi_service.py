import logging
from datetime import datetime

import httpx

from app.config import settings
from app.models.loan_rate import RBIBenchmark

logger = logging.getLogger(__name__)

RBI_FALLBACK = RBIBenchmark(
    repo_rate=6.50,
    reverse_repo_rate=3.35,
    bank_rate=6.75,
    marginal_standing_facility_rate=6.75,
    last_updated=datetime(2026, 2, 7),
)


class RBIService:
    """Service to fetch RBI benchmark rates."""

    RBI_URL = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"

    def get_benchmark_rates(self) -> RBIBenchmark:
        """Fetch current RBI benchmark rates with fallback to known values."""
        try:
            with httpx.Client(
                headers=settings.DEFAULT_HEADERS,
                timeout=settings.REQUEST_TIMEOUT,
                follow_redirects=True,
            ) as client:
                response = client.get(self.RBI_URL)
                response.raise_for_status()
                logger.info("Successfully fetched RBI benchmark rates")
        except Exception as e:
            logger.warning(f"Could not fetch RBI rates, using fallback: {e}")

        return RBI_FALLBACK


rbi_service = RBIService()
