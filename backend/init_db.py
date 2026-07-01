"""
Database initialization and data loading script
"""
import asyncio
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from src.database.core import engine, async_session_maker
from src.models import (
    Branch, LoanOfficer, Portfolio, LoanAccount, 
    CustomerDemographics, PaymentHistory, RiskMetrics
)
from sqlmodel import Session, select
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_SAMPLES_DIR = SCRIPT_DIR / "data" / "samples"


async def init_database():
    """Initialize database tables"""
    try:
        from sqlmodel import SQLModel
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def load_csv_data(filename):
    """Load CSV data"""
    data_path = DATA_SAMPLES_DIR / filename
    if data_path.exists():
        return pd.read_csv(data_path)
    else:
        logger.warning(f"File not found: {data_path}")
        return None


async def load_branches():
    """Load branches data"""
    df = load_csv_data("branches.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            branch = Branch(
                id=int(row["branch_id"]),
                branch_name=row["branch_name"],
                region=row["region"],
                manager_id=int(row["manager_id"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"])
            )
            session.add(branch)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} branches")


async def load_loan_officers():
    """Load loan officers data"""
    df = load_csv_data("loan_officers.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            officer = LoanOfficer(
                id=int(row["officer_id"]),
                officer_name=row["officer_name"],
                branch_id=int(row["branch_id"]),
                hire_date=datetime.fromisoformat(row["hire_date"]),
                region=row["region"]
            )
            session.add(officer)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} loan officers")


async def load_portfolios():
    """Load portfolios data"""
    df = load_csv_data("portfolios.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            portfolio = Portfolio(
                id=int(row["portfolio_id"]),
                portfolio_name=row["portfolio_name"],
                region=row["region"],
                branch_id=int(row["branch_id"]),
                total_exposure=float(row["total_exposure"]),
                created_at=datetime.fromisoformat(row["created_at"])
            )
            session.add(portfolio)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} portfolios")


async def load_customers():
    """Load customer demographics"""
    df = load_csv_data("customers.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            customer = CustomerDemographics(
                customer_id=row["customer_id"],
                gender=row["gender"],
                age=int(row["age"]),
                income_level=row["income_level"],
                occupation=row["occupation"],
                financial_inclusion_score=float(row["financial_inclusion_score"])
            )
            session.add(customer)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} customers")


async def load_loan_accounts():
    """Load loan accounts"""
    df = load_csv_data("loan_accounts.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            account = LoanAccount(
                id=int(row["account_id"]),
                account_number=row["account_number"],
                account_name=row["account_name"],
                portfolio_id=int(row["portfolio_id"]),
                branch_id=int(row["branch_id"]),
                officer_id=int(row["officer_id"]),
                approval_date=datetime.fromisoformat(row["approval_date"]),
                loan_amount=float(row["loan_amount"]),
                interest_rate=float(row["interest_rate"]),
                status=row["status"],
                ltv_ratio=float(row["ltv_ratio"]),
                collateral_type=row["collateral_type"]
            )
            session.add(account)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} loan accounts")


async def load_payment_history():
    """Load payment history"""
    df = load_csv_data("payment_history.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            payment = PaymentHistory(
                id=int(row["payment_id"]),
                account_id=int(row["account_id"]),
                payment_date=datetime.fromisoformat(row["payment_date"]),
                amount_paid=float(row["amount_paid"]),
                status=row["status"],
                days_past_due=int(row["days_past_due"])
            )
            session.add(payment)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} payment records")


async def load_risk_metrics():
    """Load risk metrics"""
    df = load_csv_data("risk_metrics.csv")
    if df is None:
        return
    
    async with async_session_maker() as session:
        for idx, row in df.iterrows():
            metric = RiskMetrics(
                id=int(row["metric_id"]),
                account_id=int(row["account_id"]),
                risk_date=datetime.fromisoformat(row["risk_date"]),
                par_status=row["par_status"],
                npl_flag=bool(row["npl_flag"]),
                arrears_ratio=float(row["arrears_ratio"]),
                interest_arrear=float(row["interest_arrear"]),
                restructure_count=int(row["restructure_count"]),
                risk_score=float(row["risk_score"])
            )
            session.add(metric)
        
        await session.commit()
        logger.info(f"✓ Loaded {len(df)} risk metrics")


async def main():
    """Main initialization function"""
    print("=" * 60)
    print("Database Initialization & Data Loading")
    print("=" * 60 + "\n")
    
    try:
        # Initialize database tables
        print("Creating database tables...")
        await init_database()
        
        # Load data in sequence
        print("\nLoading sample data...\n")
        await load_branches()
        await load_loan_officers()
        await load_portfolios()
        await load_customers()
        await load_loan_accounts()
        await load_payment_history()
        await load_risk_metrics()
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
