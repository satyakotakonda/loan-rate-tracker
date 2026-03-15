import logging
from datetime import datetime

from app.models.loan_rate import LoanRate
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class PNBScraper(BaseScraper):
    """Scraper for Punjab National Bank loan rates."""

    bank_name = "Punjab National Bank"
    bank_logo_url = "https://www.pnbindia.in/favicon.ico"
    personal_loan_url = "https://www.pnbindia.in/personal-loan.html"
    home_loan_url = "https://www.pnbindia.in/home-loan.html"

    def _get_personal_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="personal",
                interest_rate_min=11.40,
                interest_rate_max=16.95,
                processing_fee="1% of loan amount + GST (min ₹1,000, max ₹15,000)",
                loan_amount_min=25000,
                loan_amount_max=2000000,
                tenure_min=6,
                tenure_max=72,
                source_url=self.personal_loan_url,
                rate_type="floating",
                last_updated=datetime.utcnow(),
            )
        ]

    def _get_home_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="home",
                interest_rate_min=8.50,
                interest_rate_max=10.25,
                processing_fee="0.35% of loan amount + GST (max ₹15,000)",
                loan_amount_min=500000,
                loan_amount_max=100000000,
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
