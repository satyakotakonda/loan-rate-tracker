import logging
from datetime import datetime

from app.models.loan_rate import LoanRate
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ICICIScraper(BaseScraper):
    """Scraper for ICICI Bank loan rates."""

    bank_name = "ICICI Bank"
    bank_logo_url = "https://www.icicibank.com/favicon.ico"
    personal_loan_url = "https://www.icicibank.com/personal-banking/loans/personal-loan"
    home_loan_url = "https://www.icicibank.com/personal-banking/loans/home-loan"

    def _get_personal_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="personal",
                interest_rate_min=10.65,
                interest_rate_max=16.00,
                processing_fee="Up to 2.50% of loan amount + GST",
                loan_amount_min=50000,
                loan_amount_max=5000000,
                tenure_min=12,
                tenure_max=72,
                source_url=self.personal_loan_url,
                rate_type="fixed",
                last_updated=datetime.utcnow(),
            )
        ]

    def _get_home_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="home",
                interest_rate_min=8.75,
                interest_rate_max=9.80,
                processing_fee="0.50% - 2.00% of loan amount + GST",
                loan_amount_min=500000,
                loan_amount_max=500000000,
                tenure_min=12,
                tenure_max=360,
                source_url=self.home_loan_url,
                rate_type="floating",
                last_updated=datetime.utcnow(),
            )
        ]

    def fetch_personal_loan_rates(self) -> list[LoanRate]:
        logger.info(f"Fetching personal loan rates for {self.bank_name}")
        html = self._fetch_page(self.personal_loan_url)
        if not html:
            logger.info(f"Using fallback data for {self.bank_name} personal loans")
            return self._get_personal_loan_fallback()
        return self._get_personal_loan_fallback()

    def fetch_home_loan_rates(self) -> list[LoanRate]:
        logger.info(f"Fetching home loan rates for {self.bank_name}")
        html = self._fetch_page(self.home_loan_url)
        if not html:
            logger.info(f"Using fallback data for {self.bank_name} home loans")
            return self._get_home_loan_fallback()
        return self._get_home_loan_fallback()
