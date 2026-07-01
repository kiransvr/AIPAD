"""Financial inclusion business logic service."""
from typing import Any


def get_inclusion_summary() -> dict[str, Any]:
    """Get financial inclusion summary."""
    return {
        "inclusion_score": 78.5,
        "active_underserved": 3245,
        "rural_percentage": 42.5,
        "women_entrepreneurs": 28.3,
    }


def get_demographic_breakdown() -> dict[str, Any]:
    """Get demographic breakdown."""
    return {
        "demographics": [
            {"segment": "Rural", "accounts": 2992, "percentage": 42.5, "par": 12.3},
            {"segment": "Semi-urban", "accounts": 2246, "percentage": 31.9, "par": 10.8},
            {"segment": "Urban", "accounts": 1802, "percentage": 25.6, "par": 9.2},
        ]
    }


def get_regional_inclusion() -> dict[str, Any]:
    """Get regional inclusion metrics."""
    return {
        "regions": [
            {"name": "North", "inclusion_score": 82.5, "rural_pct": 48.2, "women_entrepreneurs": 35.1},
            {"name": "South", "inclusion_score": 76.2, "rural_pct": 38.5, "women_entrepreneurs": 28.3},
            {"name": "East", "inclusion_score": 79.8, "rural_pct": 42.1, "women_entrepreneurs": 31.5},
            {"name": "West", "inclusion_score": 75.5, "rural_pct": 40.0, "women_entrepreneurs": 27.8},
            {"name": "Central", "inclusion_score": 78.3, "rural_pct": 45.3, "women_entrepreneurs": 29.2},
        ]
    }


def get_inclusion_index() -> dict[str, Any]:
    """Get inclusion index trend."""
    return {
        "trend": [
            {"month": "January", "score": 74.2},
            {"month": "February", "score": 75.1},
            {"month": "March", "score": 76.3},
            {"month": "April", "score": 77.4},
            {"month": "May", "score": 78.5},
        ],
        "target_score": 85.0,
    }
