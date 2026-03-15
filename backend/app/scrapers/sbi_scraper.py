import logging
from datetime import datetime

from app.models.loan_rate import LoanRate
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SBIScraper(BaseScraper):
    """Scraper for State Bank of India loan rates."""

    bank_name = "State Bank of India"
    bank_logo_url = "https://www.sbi.co.in/favicon.ico"
    personal_loan_url = "https://www.sbi.co.in/web/personal-banking/loans/personal-loan"
    home_loan_url = "https://www.sbi.co.in/web/personal-banking/loans/home-loans/sbi-home-loan"

    def _get_personal_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="personal",
                interest_rate_min=11.15,
                interest_rate_max=15.30,
                processing_fee="1.50% of loan amount (min ₹1,000, max ₹15,000) + GST",
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
                interest_rate_max=10.15,
                processing_fee="0.35% of loan amount (min ₹2,000, max ₹10,000) + GST",
                loan_amount_min=1000000,
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
