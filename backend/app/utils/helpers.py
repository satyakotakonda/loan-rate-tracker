import math
from datetime import datetime
from typing import Optional


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> dict:
    """
    Calculate EMI using the standard formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)

    Args:
        principal: Loan amount in INR
        annual_rate: Annual interest rate in percentage (e.g., 10.5)
        tenure_months: Loan tenure in months

    Returns:
        dict with emi, total_interest, total_payment
    """
    monthly_rate = annual_rate / (12 * 100)

    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = (
            principal
            * monthly_rate
            * math.pow(1 + monthly_rate, tenure_months)
            / (math.pow(1 + monthly_rate, tenure_months) - 1)
        )

    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    return {
        "emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2),
    }


def format_currency(amount: float) -> str:
    """Format amount in Indian currency format (lakhs/crores)."""
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.1f} Cr"
    elif amount >= 100_000:
        return f"₹{amount / 100_000:.1f} L"
    else:
        return f"₹{amount:,.0f}"


def format_tenure(months: Optional[int]) -> Optional[str]:
    """Format tenure in years and months."""
    if months is None:
        return None
    years = months // 12
    remaining_months = months % 12
    if years and remaining_months:
        return f"{years}Y {remaining_months}M"
    elif years:
        return f"{years} Years"
    else:
        return f"{remaining_months} Months"


def get_current_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"
