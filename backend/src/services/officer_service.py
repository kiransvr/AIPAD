"""Loan officer productivity business logic service."""
from typing import Any


def get_officer_summary() -> dict[str, Any]:
    """Get loan officer productivity summary."""
    return {
        "officers": [
            {
                "id": 101,
                "name": "Rajesh Kumar",
                "branch": "Main Branch",
                "portfolio": 4500000,
                "accounts": 120,
                "par": 7.2,
                "recovery_rate": 56.2,
            },
            {
                "id": 102,
                "name": "Priya Singh",
                "branch": "Downtown",
                "portfolio": 5200000,
                "accounts": 145,
                "par": 10.5,
                "recovery_rate": 48.1,
            },
            {
                "id": 103,
                "name": "Amit Patel",
                "branch": "Midtown",
                "portfolio": 3800000,
                "accounts": 95,
                "par": 12.3,
                "recovery_rate": 42.5,
            },
            {
                "id": 104,
                "name": "Neha Verma",
                "branch": "North Point",
                "portfolio": 4100000,
                "accounts": 115,
                "par": 9.8,
                "recovery_rate": 50.3,
            },
            {
                "id": 105,
                "name": "Vikram Desai",
                "branch": "Riverside",
                "portfolio": 3200000,
                "accounts": 80,
                "par": 13.5,
                "recovery_rate": 38.9,
            },
            {
                "id": 106,
                "name": "Divya Sharma",
                "branch": "East Side",
                "portfolio": 4600000,
                "accounts": 125,
                "par": 8.5,
                "recovery_rate": 52.7,
            },
        ],
        "total_officers": 125,
        "average_portfolio_size": 3850000,
        "average_par": 10.5,
    }


def get_officer_detail(officer_id: int) -> dict[str, Any]:
    """Get specific officer details."""
    _ = officer_id
    return {}


def get_officer_leaderboard() -> dict[str, Any]:
    """Get officer productivity leaderboard."""
    return {
        "leaderboard": [
            {"rank": 1, "name": "Rajesh Kumar", "accounts": 120, "recovery_rate": 56.2, "npl_ratio": 2.1, "score": 92},
            {"rank": 2, "name": "Divya Sharma", "accounts": 125, "recovery_rate": 52.7, "npl_ratio": 2.4, "score": 89},
            {"rank": 3, "name": "Neha Verma", "accounts": 115, "recovery_rate": 50.3, "npl_ratio": 2.8, "score": 85},
            {"rank": 4, "name": "Priya Singh", "accounts": 145, "recovery_rate": 48.1, "npl_ratio": 3.2, "score": 81},
            {"rank": 5, "name": "Amit Patel", "accounts": 95, "recovery_rate": 42.5, "npl_ratio": 3.9, "score": 74},
            {"rank": 6, "name": "Vikram Desai", "accounts": 80, "recovery_rate": 38.9, "npl_ratio": 4.5, "score": 68},
        ]
    }
