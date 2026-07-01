"""
Sample data generation script for AI Portfolio Analytics Dashboard
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Create data directories relative to this script location
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR = DATA_DIR / "samples"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

print("Generating sample data for AI Portfolio Analytics Dashboard...\n")


# 1. Generate Branches Data
def generate_branches(num_branches=10):
    """Generate branch data"""
    regions = ["North", "South", "East", "West", "Central"]
    branches = []
    
    for i in range(1, num_branches + 1):
        branch = {
            "branch_id": i,
            "branch_name": f"{np.random.choice(regions)} Branch {i}",
            "region": np.random.choice(regions),
            "manager_id": i,
            "latitude": np.random.uniform(-90, 90),
            "longitude": np.random.uniform(-180, 180),
            "created_at": (datetime.now() - timedelta(days=np.random.randint(30, 365))).isoformat()
        }
        branches.append(branch)
    
    df = pd.DataFrame(branches)
    df.to_csv(SAMPLE_DIR / "branches.csv", index=False)
    print(f"✓ Generated {len(df)} branches")
    return df


# 2. Generate Loan Officers Data
def generate_loan_officers(branches_df, officers_per_branch=3):
    """Generate loan officer data"""
    officers = []
    officer_id = 1
    
    for idx, row in branches_df.iterrows():
        for j in range(officers_per_branch):
            officer = {
                "officer_id": officer_id,
                "officer_name": f"Officer_{officer_id}",
                "branch_id": row["branch_id"],
                "hire_date": (datetime.now() - timedelta(days=np.random.randint(365, 1825))).isoformat(),
                "region": row["region"]
            }
            officers.append(officer)
            officer_id += 1
    
    df = pd.DataFrame(officers)
    df.to_csv(SAMPLE_DIR / "loan_officers.csv", index=False)
    print(f"✓ Generated {len(df)} loan officers")
    return df


# 3. Generate Portfolios Data
def generate_portfolios(branches_df, portfolios_per_branch=2):
    """Generate portfolio data"""
    portfolios = []
    portfolio_id = 1
    
    for idx, row in branches_df.iterrows():
        for j in range(portfolios_per_branch):
            portfolio = {
                "portfolio_id": portfolio_id,
                "portfolio_name": f"Portfolio_{portfolio_id}",
                "region": row["region"],
                "branch_id": row["branch_id"],
                "total_exposure": np.random.uniform(100000, 5000000),
                "created_at": (datetime.now() - timedelta(days=np.random.randint(30, 365))).isoformat()
            }
            portfolios.append(portfolio)
            portfolio_id += 1
    
    df = pd.DataFrame(portfolios)
    df.to_csv(SAMPLE_DIR / "portfolios.csv", index=False)
    print(f"✓ Generated {len(df)} portfolios")
    return df


# 4. Generate Customer Demographics
def generate_customer_demographics(num_customers=500):
    """Generate customer demographic data"""
    genders = ["M", "F", "Other"]
    occupations = ["Business", "Employee", "Self-Employed", "Farmer", "Student"]
    income_levels = ["Low", "Medium", "High", "Very High"]
    
    customers = []
    
    for i in range(1, num_customers + 1):
        customer = {
            "customer_id": f"CUST_{i:06d}",
            "gender": np.random.choice(genders),
            "age": np.random.randint(18, 75),
            "income_level": np.random.choice(income_levels),
            "occupation": np.random.choice(occupations),
            "financial_inclusion_score": np.random.uniform(0, 100)
        }
        customers.append(customer)
    
    df = pd.DataFrame(customers)
    df.to_csv(SAMPLE_DIR / "customers.csv", index=False)
    print(f"✓ Generated {len(df)} customers")
    return df


# 5. Generate Loan Accounts
def generate_loan_accounts(portfolios_df, officers_df, customers_df, accounts_per_portfolio=20):
    """Generate loan account data"""
    accounts = []
    account_id = 1
    statuses = ["Active", "Closed", "Defaulted", "Restructured"]
    collateral_types = ["Land", "Building", "Equipment", "Unsecured"]
    
    for idx, portfolio in portfolios_df.iterrows():
        for j in range(accounts_per_portfolio):
            officer = officers_df[officers_df["branch_id"] == portfolio["branch_id"]].sample(1).iloc[0]
            customer = customers_df.sample(1).iloc[0]
            approval_date = datetime.now() - timedelta(days=np.random.randint(30, 730))
            
            account = {
                "account_id": account_id,
                "account_number": f"ACC_{account_id:08d}",
                "account_name": f"Loan_{account_id}",
                "portfolio_id": portfolio["portfolio_id"],
                "branch_id": portfolio["branch_id"],
                "officer_id": officer["officer_id"],
                "customer_id": customer["customer_id"],
                "approval_date": approval_date.isoformat(),
                "loan_amount": np.random.uniform(5000, 500000),
                "interest_rate": np.random.uniform(0.05, 0.25),
                "status": np.random.choice(statuses, p=[0.70, 0.15, 0.10, 0.05]),
                "ltv_ratio": np.random.uniform(0.3, 0.9),
                "collateral_type": np.random.choice(collateral_types)
            }
            accounts.append(account)
            account_id += 1
    
    df = pd.DataFrame(accounts)
    df.to_csv(SAMPLE_DIR / "loan_accounts.csv", index=False)
    print(f"✓ Generated {len(df)} loan accounts")
    return df


# 6. Generate Payment History
def generate_payment_history(accounts_df):
    """Generate payment history data"""
    payments = []
    payment_id = 1
    payment_statuses = ["On-time", "Late", "Arrears"]
    
    for idx, account in accounts_df.iterrows():
        approval_date = datetime.fromisoformat(account["approval_date"])
        num_payments = np.random.randint(1, 36)  # Up to 36 months of payments
        
        for month in range(num_payments):
            payment_date = approval_date + timedelta(days=30 * month)
            
            if payment_date > datetime.now():
                continue
            
            # Determine payment status based on days overdue
            days_overdue = (datetime.now() - payment_date).days
            if days_overdue < 30:
                status = "On-time"
            elif days_overdue < 60:
                status = "Late"
            else:
                status = "Arrears"
            
            payment = {
                "payment_id": payment_id,
                "account_id": account["account_id"],
                "payment_date": payment_date.isoformat(),
                "amount_paid": account["loan_amount"] / num_payments if status == "On-time" else 0,
                "status": status,
                "days_past_due": max(0, days_overdue)
            }
            payments.append(payment)
            payment_id += 1
    
    df = pd.DataFrame(payments)
    df.to_csv(SAMPLE_DIR / "payment_history.csv", index=False)
    print(f"✓ Generated {len(df)} payment records")
    return df


# 7. Generate Risk Metrics
def generate_risk_metrics(accounts_df):
    """Generate risk metrics data"""
    metrics = []
    metric_id = 1
    par_statuses = ["0-30", "31-60", "61-90", "91-180", "180+"]
    
    for idx, account in accounts_df.iterrows():
        approval_date = datetime.fromisoformat(account["approval_date"])
        num_snapshots = np.random.randint(3, 12)  # Multiple risk snapshots
        
        for month in range(num_snapshots):
            risk_date = approval_date + timedelta(days=30 * month)
            
            if risk_date > datetime.now():
                continue
            
            # Generate risk metrics based on status
            if account["status"] == "Defaulted":
                npl_flag = True
                risk_score = np.random.uniform(0.7, 1.0)
                par_status = "180+"
                arrears_ratio = np.random.uniform(0.5, 1.0)
            elif account["status"] == "Restructured":
                npl_flag = np.random.choice([True, False], p=[0.3, 0.7])
                risk_score = np.random.uniform(0.4, 0.7)
                par_status = np.random.choice(par_statuses[:3])
                arrears_ratio = np.random.uniform(0.2, 0.5)
            else:
                npl_flag = False
                risk_score = np.random.uniform(0, 0.5)
                par_status = np.random.choice(par_statuses, p=[0.6, 0.2, 0.1, 0.07, 0.03])
                arrears_ratio = np.random.uniform(0, 0.2)
            
            metric = {
                "metric_id": metric_id,
                "account_id": account["account_id"],
                "risk_date": risk_date.isoformat(),
                "par_status": par_status,
                "npl_flag": npl_flag,
                "arrears_ratio": arrears_ratio,
                "interest_arrear": account["loan_amount"] * 0.02 * arrears_ratio if arrears_ratio > 0 else 0,
                "restructure_count": 1 if account["status"] == "Restructured" else 0,
                "risk_score": risk_score
            }
            metrics.append(metric)
            metric_id += 1
    
    df = pd.DataFrame(metrics)
    df.to_csv(SAMPLE_DIR / "risk_metrics.csv", index=False)
    print(f"✓ Generated {len(df)} risk metrics records")
    return df


# 8. Generate Summary Statistics
def generate_summary_statistics(accounts_df, payments_df, risk_df):
    """Generate summary statistics"""
    summary = {
        "total_accounts": len(accounts_df),
        "total_portfolio_amount": accounts_df["loan_amount"].sum(),
        "average_loan_size": accounts_df["loan_amount"].mean(),
        "total_payments": payments_df["amount_paid"].sum(),
        "active_accounts": len(accounts_df[accounts_df["status"] == "Active"]),
        "defaulted_accounts": len(accounts_df[accounts_df["status"] == "Defaulted"]),
        "npl_accounts": len(risk_df[risk_df["npl_flag"] == True].groupby("account_id")),
        "total_payment_records": len(payments_df),
        "total_risk_snapshots": len(risk_df),
        "generated_at": datetime.now().isoformat()
    }
    
    with open(SAMPLE_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 Summary Statistics:")
    print(f"   - Total Accounts: {summary['total_accounts']}")
    print(f"   - Total Portfolio: ${summary['total_portfolio_amount']:,.2f}")
    print(f"   - Average Loan: ${summary['average_loan_size']:,.2f}")
    print(f"   - Active Accounts: {summary['active_accounts']}")
    print(f"   - Defaulted Accounts: {summary['defaulted_accounts']}")
    print(f"   - NPL Accounts: {summary['npl_accounts']}")


# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("AI Portfolio Analytics Dashboard - Data Generation")
    print("=" * 60 + "\n")
    
    # Generate data in sequence
    branches_df = generate_branches(num_branches=10)
    officers_df = generate_loan_officers(branches_df, officers_per_branch=3)
    portfolios_df = generate_portfolios(branches_df, portfolios_per_branch=2)
    customers_df = generate_customer_demographics(num_customers=500)
    accounts_df = generate_loan_accounts(portfolios_df, officers_df, customers_df, accounts_per_portfolio=20)
    payments_df = generate_payment_history(accounts_df)
    risk_df = generate_risk_metrics(accounts_df)
    
    generate_summary_statistics(accounts_df, payments_df, risk_df)
    
    print(f"\n✅ All sample data generated successfully!")
    print(f"📂 Data location: {SAMPLE_DIR}")
    print(f"\nFiles created:")
    for file in sorted(SAMPLE_DIR.glob("*.csv")):
        print(f"   - {file.name}")
    print(f"   - summary.json")
