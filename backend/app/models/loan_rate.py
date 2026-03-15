from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoanRate(BaseModel):
    bank_name: str
    bank_logo_url: Optional[str] = None
    loan_type: str  # "personal" or "home"
    interest_rate_min: float
    interest_rate_max: float
    processing_fee: Optional[str] = None
    loan_amount_min: Optional[float] = None
    loan_amount_max: Optional[float] = None
    tenure_min: Optional[int] = None  # in months
    tenure_max: Optional[int] = None  # in months
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    source_url: Optional[str] = None
    rate_type: str = "floating"  # "fixed" or "floating"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RBIBenchmark(BaseModel):
    repo_rate: float
    reverse_repo_rate: float
    bank_rate: float
    marginal_standing_facility_rate: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class EMICalculationRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan principal amount in INR")
    rate: float = Field(..., gt=0, description="Annual interest rate in percentage")
    tenure: int = Field(..., gt=0, description="Loan tenure in months")


class EMICalculation(BaseModel):
    principal: float
    rate: float
    tenure: int
    emi: float
    total_interest: float
    total_payment: float


class RatesResponse(BaseModel):
    data: list[LoanRate]
    total: int
    last_refreshed: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BestRatesResponse(BaseModel):
    best_personal_loan: Optional[LoanRate] = None
    best_home_loan: Optional[LoanRate] = None
    personal_loans_sorted: list[LoanRate] = []
    home_loans_sorted: list[LoanRate] = []
