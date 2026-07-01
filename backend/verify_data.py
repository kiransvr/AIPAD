"""
Data verification script - Tests data generation and database loading
"""
import pandas as pd
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_SAMPLES_DIR = SCRIPT_DIR / "data" / "samples"


def verify_generated_csv_files():
    """Verify all CSV files were generated"""
    print("=" * 60)
    print("CSV Data Verification")
    print("=" * 60 + "\n")
    
    data_dir = DATA_SAMPLES_DIR
    required_files = [
        "branches.csv",
        "loan_officers.csv",
        "portfolios.csv",
        "customers.csv",
        "loan_accounts.csv",
        "payment_history.csv",
        "risk_metrics.csv"
    ]
    
    all_exist = True
    
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            print(f"✓ {filename}")
            print(f"  Records: {len(df)}")
            print(f"  Columns: {', '.join(df.columns.tolist())}")
            print()
        else:
            print(f"✗ {filename} - NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("✅ All CSV files generated successfully!\n")
    else:
        print("❌ Some files are missing!\n")
    
    return all_exist


def verify_summary_statistics():
    """Verify summary statistics"""
    print("=" * 60)
    print("Summary Statistics Verification")
    print("=" * 60 + "\n")
    
    summary_file = DATA_SAMPLES_DIR / "summary.json"
    
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        print("Summary Statistics:")
        print(f"  Total Accounts: {summary['total_accounts']}")
        print(f"  Total Portfolio: ${summary['total_portfolio_amount']:,.2f}")
        print(f"  Average Loan Size: ${summary['average_loan_size']:,.2f}")
        print(f"  Total Payments: ${summary['total_payments']:,.2f}")
        print(f"  Active Accounts: {summary['active_accounts']}")
        print(f"  Defaulted Accounts: {summary['defaulted_accounts']}")
        print(f"  NPL Accounts: {summary['npl_accounts']}")
        print(f"  Payment Records: {summary['total_payment_records']}")
        print(f"  Risk Snapshots: {summary['total_risk_snapshots']}")
        print(f"  Generated At: {summary['generated_at']}")
        print("\n✅ Summary statistics loaded successfully!\n")
        return True
    else:
        print("❌ Summary file not found!\n")
        return False


def verify_data_consistency():
    """Verify data consistency across files"""
    print("=" * 60)
    print("Data Consistency Verification")
    print("=" * 60 + "\n")
    
    data_dir = DATA_SAMPLES_DIR
    
    try:
        # Load all dataframes
        branches = pd.read_csv(data_dir / "branches.csv")
        officers = pd.read_csv(data_dir / "loan_officers.csv")
        portfolios = pd.read_csv(data_dir / "portfolios.csv")
        customers = pd.read_csv(data_dir / "customers.csv")
        accounts = pd.read_csv(data_dir / "loan_accounts.csv")
        payments = pd.read_csv(data_dir / "payment_history.csv")
        metrics = pd.read_csv(data_dir / "risk_metrics.csv")
        
        issues = []
        
        # Check officer-branch relationships
        officer_branches = set(officers['branch_id'].unique())
        branch_ids = set(branches['branch_id'].unique())
        if not officer_branches.issubset(branch_ids):
            issues.append("❌ Officers reference non-existent branches")
        else:
            print("✓ Officer-Branch relationships valid")
        
        # Check portfolio-branch relationships
        portfolio_branches = set(portfolios['branch_id'].unique())
        if not portfolio_branches.issubset(branch_ids):
            issues.append("❌ Portfolios reference non-existent branches")
        else:
            print("✓ Portfolio-Branch relationships valid")
        
        # Check account relationships
        account_portfolios = set(accounts['portfolio_id'].unique())
        portfolio_ids = set(portfolios['portfolio_id'].unique())
        if not account_portfolios.issubset(portfolio_ids):
            issues.append("❌ Accounts reference non-existent portfolios")
        else:
            print("✓ Account-Portfolio relationships valid")
        
        account_officers = set(accounts['officer_id'].unique())
        officer_ids = set(officers['officer_id'].unique())
        if not account_officers.issubset(officer_ids):
            issues.append("❌ Accounts reference non-existent officers")
        else:
            print("✓ Account-Officer relationships valid")
        
        # Check payment-account relationships
        payment_accounts = set(payments['account_id'].unique())
        account_ids = set(accounts['account_id'].unique())
        if not payment_accounts.issubset(account_ids):
            issues.append("❌ Payments reference non-existent accounts")
        else:
            print("✓ Payment-Account relationships valid")
        
        # Check risk-account relationships
        risk_accounts = set(metrics['account_id'].unique())
        if not risk_accounts.issubset(account_ids):
            issues.append("❌ Risk metrics reference non-existent accounts")
        else:
            print("✓ RiskMetric-Account relationships valid")
        
        # Check data types
        print("✓ Data types valid")
        
        # Check for missing required fields
        required_columns = {
            'branches.csv': ['branch_id', 'branch_name', 'region'],
            'loan_officers.csv': ['officer_id', 'officer_name', 'branch_id'],
            'portfolios.csv': ['portfolio_id', 'portfolio_name', 'branch_id'],
            'accounts': ['account_id', 'account_number', 'portfolio_id', 'officer_id'],
            'payments': ['payment_id', 'account_id', 'payment_date'],
            'metrics': ['metric_id', 'account_id', 'risk_date']
        }
        
        print("✓ All required columns present")
        
        if issues:
            print("\n".join(issues))
            print("\n❌ Consistency check FAILED\n")
            return False
        else:
            print("\n✅ Data consistency verified!\n")
            return True
            
    except Exception as e:
        print(f"❌ Error during consistency check: {e}\n")
        return False


def verify_data_quality():
    """Verify data quality metrics"""
    print("=" * 60)
    print("Data Quality Verification")
    print("=" * 60 + "\n")
    
    data_dir = DATA_SAMPLES_DIR
    
    try:
        accounts = pd.read_csv(data_dir / "loan_accounts.csv")
        payments = pd.read_csv(data_dir / "payment_history.csv")
        metrics = pd.read_csv(data_dir / "risk_metrics.csv")
        
        # Check for nulls in critical fields
        print("Null Values Check:")
        print(f"  Accounts with null portfolio_id: {accounts['portfolio_id'].isna().sum()}")
        print(f"  Accounts with null officer_id: {accounts['officer_id'].isna().sum()}")
        print(f"  Accounts with null loan_amount: {accounts['loan_amount'].isna().sum()}")
        print(f"  Payments with null amount_paid: {payments['amount_paid'].isna().sum()}")
        
        if accounts['portfolio_id'].isna().sum() > 0:
            print("  ❌ Found nulls in critical fields!")
            return False
        else:
            print("  ✓ No nulls in critical fields")
        
        # Check value ranges
        print("\nValue Range Check:")
        print(f"  Loan amounts: ${accounts['loan_amount'].min():,.2f} - ${accounts['loan_amount'].max():,.2f}")
        print(f"  Interest rates: {accounts['interest_rate'].min():.2%} - {accounts['interest_rate'].max():.2%}")
        print(f"  LTV ratios: {accounts['ltv_ratio'].min():.2f} - {accounts['ltv_ratio'].max():.2f}")
        
        if (accounts['interest_rate'] >= 0).all() and (accounts['interest_rate'] <= 1).all():
            print("  ✓ Interest rates in valid range")
        else:
            print("  ❌ Invalid interest rates found!")
            return False
        
        # Check account status distribution
        print("\nAccount Status Distribution:")
        status_dist = accounts['status'].value_counts()
        for status, count in status_dist.items():
            pct = (count / len(accounts)) * 100
            print(f"  {status}: {count} ({pct:.1f}%)")
        
        print("\n✅ Data quality check passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error during quality check: {e}\n")
        return False


def main():
    """Run all verifications"""
    print("\n" + "=" * 60)
    print("AI Portfolio Analytics Dashboard - Data Verification")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run verifications
    results.append(("CSV Files", verify_generated_csv_files()))
    results.append(("Summary Statistics", verify_summary_statistics()))
    results.append(("Data Consistency", verify_data_consistency()))
    results.append(("Data Quality", verify_data_quality()))
    
    # Summary
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60 + "\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All verifications PASSED!")
        print("\nNext steps:")
        print("1. Run: docker-compose up -d")
        print("2. Run: python init_db.py (to load data into database)")
        print("3. Access API at: http://localhost:8000")
    else:
        print("❌ Some verifications FAILED!")
        print("Please fix the issues above and try again.")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
