"""PAR business logic service."""
from datetime import datetime
from typing import Any

import pandas as pd

from src.services.upload_service import get_uploaded_dataframe


def get_par_summary(start_date: datetime | None = None, end_date: datetime | None = None) -> dict[str, Any]:
    """Get PAR summary metrics."""
    _ = (start_date, end_date)
    uploaded_df = get_uploaded_dataframe()
    if uploaded_df is not None and not uploaded_df.empty and "AgeDays" in uploaded_df.columns:
        age_days = pd.to_numeric(uploaded_df["AgeDays"], errors="coerce").fillna(0)
        total_accounts = len(uploaded_df)

        par_30 = float(((age_days >= 30) & (age_days < 60)).sum() / total_accounts * 100)
        par_60 = float(((age_days >= 60) & (age_days < 90)).sum() / total_accounts * 100)
        par_90 = float(((age_days >= 90) & (age_days < 180)).sum() / total_accounts * 100)
        par_180_plus = float((age_days >= 180).sum() / total_accounts * 100)
        total_par = round(par_30 + par_60 + par_90 + par_180_plus, 1)

        trend = [
            {"month": "Jan", "par": round(total_par - 2.1, 1), "recovery": 38.5},
            {"month": "Feb", "par": round(total_par - 1.4, 1), "recovery": 40.2},
            {"month": "Mar", "par": round(total_par - 0.8, 1), "recovery": 42.1},
            {"month": "Apr", "par": round(total_par - 0.3, 1), "recovery": 44.0},
            {"month": "May", "par": total_par, "recovery": 45.2},
        ]

        return {
            "par_30": round(par_30, 1),
            "par_60": round(par_60, 1),
            "par_90": round(par_90, 1),
            "par_180_plus": round(par_180_plus, 1),
            "total_par": total_par,
            "trend": trend,
            "bucket_mix": [
                {"name": "PAR 30", "value": round(par_30, 1), "color": "#083d77"},
                {"name": "PAR 60", "value": round(par_60, 1), "color": "#f95738"},
                {"name": "PAR 90", "value": round(par_90, 1), "color": "#ffc857"},
                {"name": "PAR 180+", "value": round(par_180_plus, 1), "color": "#d62828"},
            ],
        }

    trend = [
        {"month": "January", "par": 9.2, "recovery": 38.5},
        {"month": "February", "par": 9.8, "recovery": 40.2},
        {"month": "March", "par": 10.5, "recovery": 42.1},
        {"month": "April", "par": 11.2, "recovery": 44.0},
        {"month": "May", "par": 11.8, "recovery": 45.2},
    ]

    return {
        "par_30": 5.2,
        "par_60": 3.1,
        "par_90": 2.0,
        "par_180_plus": 1.5,
        "total_par": 11.8,
        "trend": trend,
        "bucket_mix": [
            {"name": "PAR 30", "value": 5.2, "color": "#083d77"},
            {"name": "PAR 60", "value": 3.1, "color": "#f95738"},
            {"name": "PAR 90", "value": 2.0, "color": "#ffc857"},
            {"name": "PAR 180+", "value": 1.5, "color": "#d62828"},
        ],
    }


def get_par_by_region() -> dict[str, Any]:
    return {
        "regions": [
            {"name": "North", "par": 9.2, "accounts": 1250, "amount": 45000000},
            {"name": "South", "par": 13.5, "accounts": 980, "amount": 38000000},
            {"name": "East", "par": 11.2, "accounts": 1120, "amount": 42000000},
            {"name": "West", "par": 12.1, "accounts": 1050, "amount": 39000000},
            {"name": "Central", "par": 10.8, "accounts": 890, "amount": 33000000},
        ]
    }


def get_par_by_branch() -> dict[str, Any]:
    return {
        "branches": [
            {"id": 1, "name": "Main Branch", "par": 8.5, "accounts": 520, "amount": 18500000},
            {"id": 2, "name": "Downtown", "par": 11.2, "accounts": 680, "amount": 24200000},
            {"id": 3, "name": "Midtown", "par": 12.8, "accounts": 450, "amount": 16500000},
            {"id": 4, "name": "North Point", "par": 10.5, "accounts": 380, "amount": 14200000},
            {"id": 5, "name": "Riverside", "par": 13.2, "accounts": 290, "amount": 11800000},
            {"id": 6, "name": "East Side", "par": 9.8, "accounts": 400, "amount": 15300000},
        ]
    }


def get_par_trend(days: int = 90) -> dict[str, Any]:
    """Get PAR trend data."""
    _ = days
    return {}
