"""Gender analytics business logic service."""
from typing import Any


def get_gender_summary() -> dict[str, Any]:
    """Get gender analytics summary."""
    return {
        "male_percentage": 65.5,
        "female_percentage": 32.8,
        "other_percentage": 1.7,
        "total_borrowers": 5432,
    }


def get_gender_performance() -> dict[str, Any]:
    """Compare performance metrics by gender."""
    return {
        "by_gender": [
            {"gender": "Male", "par": 10.5, "recovery_rate": 46.2, "npl_ratio": 3.2, "accounts": 3549},
            {"gender": "Female", "par": 12.8, "recovery_rate": 44.1, "npl_ratio": 3.8, "accounts": 2240},
            {"gender": "Other", "par": 11.2, "recovery_rate": 45.5, "npl_ratio": 3.5, "accounts": 92},
        ]
    }


def get_gender_trend() -> dict[str, Any]:
    """Get gender inclusion trend."""
    return {
        "trend": [
            {"month": "January", "male_pct": 63.5, "female_pct": 34.2, "other_pct": 2.3},
            {"month": "February", "male_pct": 64.0, "female_pct": 33.8, "other_pct": 2.2},
            {"month": "March", "male_pct": 64.5, "female_pct": 33.2, "other_pct": 2.3},
            {"month": "April", "male_pct": 65.0, "female_pct": 33.0, "other_pct": 2.0},
            {"month": "May", "male_pct": 65.5, "female_pct": 32.8, "other_pct": 1.7},
        ]
    }
