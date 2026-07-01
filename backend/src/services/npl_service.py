"""NPL business logic service."""
from typing import Any

import pandas as pd

from src.services.upload_service import get_uploaded_dataframe


def get_npl_summary() -> dict[str, Any]:
    uploaded_df = get_uploaded_dataframe()
    if uploaded_df is not None and not uploaded_df.empty and "AgeDays" in uploaded_df.columns:
        age_days = pd.to_numeric(uploaded_df["AgeDays"], errors="coerce").fillna(0)
        balances = pd.to_numeric(uploaded_df.get("OutstandingBalance", 0), errors="coerce").fillna(0)
        npl_mask = age_days >= 90
        npl_count = int(npl_mask.sum())
        npl_amount = float(balances[npl_mask].sum())
        total_accounts = len(uploaded_df)
        npl_ratio = round((npl_count / total_accounts * 100) if total_accounts else 0, 1)
        recovery_rate = round(max(0.0, 100.0 - npl_ratio), 1)
        return {
            "npl_count": npl_count,
            "npl_amount": npl_amount,
            "npl_ratio": npl_ratio,
            "recovery_rate": recovery_rate,
        }

    return {
        "npl_count": 245,
        "npl_amount": 1250000.00,
        "npl_ratio": 3.5,
        "recovery_rate": 45.2,
    }


def get_npl_by_stage() -> dict[str, Any]:
    return {
        "stages": [
            {"stage": "PL (Provision Loss)", "count": 85, "amount": 420000, "percentage": 33.6},
            {"stage": "SL (Standard Loss)", "count": 95, "amount": 530000, "percentage": 42.4},
            {"stage": "DL (Default Loss)", "count": 65, "amount": 300000, "percentage": 24.0},
        ]
    }


def get_collections_pipeline() -> dict[str, Any]:
    uploaded_df = get_uploaded_dataframe()
    if uploaded_df is not None and not uploaded_df.empty and "AgeDays" in uploaded_df.columns:
        age_days = pd.to_numeric(uploaded_df["AgeDays"], errors="coerce").fillna(0)
        balances = pd.to_numeric(uploaded_df.get("OutstandingBalance", 0), errors="coerce").fillna(0)

        initial_contact = int(((age_days >= 1) & (age_days < 30)).sum())
        in_negotiation = int(((age_days >= 30) & (age_days < 60)).sum())
        partial_payment = int(((age_days >= 60) & (age_days < 90)).sum())
        full_recovery = int((age_days < 30).sum())

        return {
            "pipeline": [
                {
                    "stage": "Initial Contact",
                    "count": initial_contact,
                    "recovery_amount": float(balances[(age_days >= 1) & (age_days < 30)].sum()),
                },
                {
                    "stage": "In Negotiation",
                    "count": in_negotiation,
                    "recovery_amount": float(balances[(age_days >= 30) & (age_days < 60)].sum()),
                },
                {
                    "stage": "Partial Payment",
                    "count": partial_payment,
                    "recovery_amount": float(balances[(age_days >= 60) & (age_days < 90)].sum()),
                },
                {
                    "stage": "Full Recovery",
                    "count": full_recovery,
                    "recovery_amount": float(balances[age_days < 30].sum()),
                },
            ],
            "total_recovered": float(balances[age_days < 30].sum()),
            "recovery_velocity": "$0/month",
        }

    return {
        "pipeline": [
            {"stage": "Initial Contact", "count": 245, "recovery_amount": 0},
            {"stage": "In Negotiation", "count": 98, "recovery_amount": 125000},
            {"stage": "Partial Payment", "count": 52, "recovery_amount": 285000},
            {"stage": "Full Recovery", "count": 28, "recovery_amount": 563000},
        ],
        "total_recovered": 563000,
        "recovery_velocity": "$89,500/month",
    }
