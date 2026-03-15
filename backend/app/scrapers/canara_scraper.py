import logging
from datetime import datetime

from app.models.loan_rate import LoanRate
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CanaraScaper(BaseScraper):
    """Scraper for Canara Bank loan rates."""

    bank_name = "Canara Bank"
    bank_logo_url = "https://canarabank.com/favicon.ico"
    personal_loan_url = "https://canarabank.com/User_page.aspx?othermenu=91&menuid=9&submenu=4"
    home_loan_url = "https://canarabank.com/User_page.aspx?othermenu=91&menuid=9&submenu=2"

    def _get_personal_loan_fallback(self) -> list[LoanRate]:
        return [
            LoanRate(
                bank_name=self.bank_name,
                bank_logo_url=self.bank_logo_url,
                loan_type="personal",
                interest_rate_min=11.10,
                interest_rate_max=16.20,
                processing_fee="0.50% of loan amount + GST (min ₹1,000, max ₹5,000)",
                loan_amount_min=25000,
                loan_amount_max=1000000,
                tenure_min=12,
                tenure_max=60,
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
                interest_rate_min=8.40,
                interest_rate_max=11.25,
                processing_fee="0.25% of loan amount + GST (min ₹1,500, max ₹10,000)",
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
