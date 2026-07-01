"""Portfolio growth business logic service."""
from typing import Any


def get_growth_summary() -> dict[str, Any]:
    """Get portfolio growth summary."""
    return {
        "ytd_growth": 12.5,
        "active_accounts": 7040,
        "total_portfolio": 100300000,
        "average_loan_size": 14250,
        "new_accounts_month": 285,
        "new_accounts_ytd": 1420,
        "growth_rate_monthly": 4.2,
    }


def get_growth_trend(period: str = "monthly") -> dict[str, Any]:
    """Get portfolio growth trend."""
    _ = period
    return {
        "monthly_trend": [
            {"month": "January", "accounts": 6200, "portfolio": 89200000},
            {"month": "February", "accounts": 6380, "portfolio": 91500000},
            {"month": "March", "accounts": 6520, "portfolio": 93800000},
            {"month": "April", "accounts": 6750, "portfolio": 96200000},
            {"month": "May", "accounts": 7040, "portfolio": 100300000},
        ]
    }


def get_growth_forecast(months: int = 12) -> dict[str, Any]:
    """Get portfolio growth forecast."""
    _ = months
    return {}


def get_product_mix() -> dict[str, Any]:
    """Get product mix analysis."""
    return {
        "products": [
            {"name": "Personal Loans", "accounts": 3200, "portfolio": 35400000, "percentage": 35.3},
            {"name": "Business Loans", "accounts": 2100, "portfolio": 28500000, "percentage": 28.4},
            {"name": "Agricultural Loans", "accounts": 1200, "portfolio": 18200000, "percentage": 18.1},
            {"name": "Home Loans", "accounts": 540, "portfolio": 18200000, "percentage": 18.1},
        ]
    }
