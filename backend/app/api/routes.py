import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.loan_rate import (
    BestRatesResponse,
    EMICalculation,
    EMICalculationRequest,
    RBIBenchmark,
    RatesResponse,
)
from app.services.rate_aggregator import rate_aggregator
from app.services.rbi_service import rbi_service
from app.utils.helpers import calculate_emi

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["loan-rates"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Loan Rate Tracker API"}


@router.get("/rates", response_model=RatesResponse)
async def get_all_rates(
    loan_type: Optional[str] = Query(None, description="Filter by loan type: personal or home"),
    bank_name: Optional[str] = Query(None, description="Filter by bank name (partial match)"),
    sort_by: Optional[str] = Query("interest_rate_min", description="Sort by field"),
    order: str = Query("asc", description="Sort order: asc or desc"),
):
    """Get all loan rates with optional filters."""
    return rate_aggregator.get_filtered_rates(
        loan_type=loan_type,
        bank_name=bank_name,
        sort_by=sort_by,
        order=order,
    )


@router.get("/rates/personal-loan", response_model=RatesResponse)
async def get_personal_loan_rates():
    """Get personal loan rates from all banks, sorted by lowest rate."""
    return rate_aggregator.get_personal_loan_rates()


@router.get("/rates/home-loan", response_model=RatesResponse)
async def get_home_loan_rates():
    """Get home loan rates from all banks, sorted by lowest rate."""
    return rate_aggregator.get_home_loan_rates()


@router.get("/rates/best", response_model=BestRatesResponse)
async def get_best_rates():
    """Get best (lowest) rates for each loan type across all banks."""
    return rate_aggregator.get_best_rates()


@router.get("/rates/bank/{bank_name}", response_model=RatesResponse)
async def get_rates_by_bank(bank_name: str):
    """Get all loan rates for a specific bank."""
    result = rate_aggregator.get_rates_by_bank(bank_name)
    if not result.data:
        raise HTTPException(status_code=404, detail=f"No rates found for bank: {bank_name}")
    return result


@router.get("/rbi/benchmark", response_model=RBIBenchmark)
async def get_rbi_benchmark():
    """Get current RBI benchmark rates (repo rate, reverse repo, bank rate, MCLR)."""
    return rbi_service.get_benchmark_rates()


@router.post("/calculator/emi", response_model=EMICalculation)
async def calculate_emi_endpoint(request: EMICalculationRequest):
    """Calculate EMI for given principal, interest rate, and tenure."""
    result = calculate_emi(request.principal, request.rate, request.tenure)
    return EMICalculation(
        principal=request.principal,
        rate=request.rate,
        tenure=request.tenure,
        **result,
    )


@router.post("/rates/refresh")
async def refresh_rates():
    """Force refresh of cached rates from all banks."""
    rate_aggregator.get_all_rates(force_refresh=True)
    return {"message": "Rates refreshed successfully"}
