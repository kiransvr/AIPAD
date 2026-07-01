"""
Database models
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, Float, Integer, String


class Portfolio(SQLModel, table=True):
    """Portfolio model"""
    __tablename__ = "portfolios"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_name: str = Field(index=True)
    region: str = Field(index=True)
    branch_id: int = Field(foreign_key="branches.id")
    total_exposure: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LoanAccount(SQLModel, table=True):
    """Loan account model"""
    __tablename__ = "loan_accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    account_number: str = Field(index=True, unique=True)
    account_name: str
    portfolio_id: int = Field(foreign_key="portfolios.id")
    branch_id: int = Field(foreign_key="branches.id")
    officer_id: int = Field(foreign_key="loan_officers.id")
    approval_date: datetime
    loan_amount: float
    interest_rate: float
    status: str = Field(index=True)  # Active, Closed, Defaulted
    ltv_ratio: float
    collateral_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Branch(SQLModel, table=True):
    """Branch model"""
    __tablename__ = "branches"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    branch_name: str = Field(index=True)
    region: str = Field(index=True)
    manager_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LoanOfficer(SQLModel, table=True):
    """Loan officer model"""
    __tablename__ = "loan_officers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    officer_name: str = Field(index=True)
    branch_id: int = Field(foreign_key="branches.id")
    hire_date: datetime
    region: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerDemographics(SQLModel, table=True):
    """Customer demographics model"""
    __tablename__ = "customer_demographics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: str = Field(index=True, unique=True)
    gender: Optional[str] = Field(index=True)
    age: Optional[int] = None
    income_level: Optional[str] = None
    occupation: Optional[str] = None
    financial_inclusion_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentHistory(SQLModel, table=True):
    """Payment history model"""
    __tablename__ = "payment_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="loan_accounts.id", index=True)
    payment_date: datetime = Field(index=True)
    amount_paid: float
    status: str  # On-time, Late, Arrears
    days_past_due: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RiskMetrics(SQLModel, table=True):
    """Risk metrics model"""
    __tablename__ = "risk_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="loan_accounts.id", index=True)
    risk_date: datetime = Field(index=True)
    par_status: str  # 0-30, 31-60, 61-90, 91-180, 180+
    npl_flag: bool = False
    arrears_ratio: float
    interest_arrear: float
    restructure_count: int = 0
    risk_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KPISnapshot(SQLModel, table=True):
    """KPI snapshot model for caching aggregated metrics"""
    __tablename__ = "kpi_snapshots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_date: datetime = Field(index=True)
    metric_type: str = Field(index=True)  # par, npl, branch, officer, etc.
    metric_scope: str  # global, region, branch, officer
    scope_id: Optional[str] = None
    metric_value: float
    metadata_json: Optional[str] = Field(default=None, sa_column=Column("metadata", String))  # JSON payload
    created_at: datetime = Field(default_factory=datetime.utcnow)
