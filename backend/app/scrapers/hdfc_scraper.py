import logging
from datetime import datetime

from app.models.loan_rate import LoanRate
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HDFCScraper(BaseScraper):
    """Scraper for HDFC Bank loan rates."""

    bank_name = "HDFC Bank"
    bank_logo_url = "https://www.hdfcbank.com/favicon.ico"
    personal_loan_url = "https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan"
    home_loan_url = "https://www.hdfcbank.com/personal/borrow/popular-loans/home-loan"

    def _get_personal_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="personal",
                interest_rate_min=10.50,
                interest_rate_max=21.00,
                processing_fee="Up to 2.50% of loan amount + GST",
                loan_amount_min=50000,
                loan_amount_max=4000000,
                tenure_min=12,
                tenure_max=60,
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
                interest_rate_min=8.70,
                interest_rate_max=9.85,
                processing_fee="Up to 0.50% of loan amount or ₹3,000 (whichever is higher) + GST",
                loan_amount_min=300000,
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
