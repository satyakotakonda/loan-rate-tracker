import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.config import settings
from app.models.loan_rate import LoanRate

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all bank scrapers."""

    bank_name: str = ""
    bank_logo_url: Optional[str] = None
    personal_loan_url: str = ""
    home_loan_url: str = ""

    def __init__(self):
        self.client = httpx.Client(
            headers=settings.DEFAULT_HEADERS,
            timeout=settings.REQUEST_TIMEOUT,
            follow_redirects=True,
        )

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL with error handling."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching {url} for {self.bank_name}")
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP {e.response.status_code} fetching {url} for {self.bank_name}")
        except Exception as e:
            logger.warning(f"Error fetching {url} for {self.bank_name}: {e}")
        return None

    @abstractmethod
    def fetch_personal_loan_rates(self) -> list[LoanRate]:
        """Fetch personal loan rates for this bank."""
        pass

    @abstractmethod
    def fetch_home_loan_rates(self) -> list[LoanRate]:
        """Fetch home loan rates for this bank."""
        pass

    def get_all_rates(self) -> list[LoanRate]:
        """Fetch all loan rates (personal + home) for this bank."""
        rates = []
        try:
            personal_rates = self.fetch_personal_loan_rates()
            rates.extend(personal_rates)
        except Exception as e:
            logger.error(f"Error fetching personal loan rates for {self.bank_name}: {e}")

        try:
            home_rates = self.fetch_home_loan_rates()
            rates.extend(home_rates)
        except Exception as e:
            logger.error(f"Error fetching home loan rates for {self.bank_name}: {e}")

        return rates

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass
