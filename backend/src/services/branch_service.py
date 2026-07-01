"""Branch analytics business logic service."""
from typing import Any


def get_branch_summary() -> dict[str, Any]:
    """Get all branch performance summary."""
    return {
        "branches": [
            {
                "id": 1,
                "name": "Addis Ababa - Bole",
                "manager_name": "Abebe Kebede",
                "par": 7.9,
                "npl_ratio": 2.4,
                "portfolio": 2850000000,
                "accounts": 910,
                "recovery_rate": 58.1,
            },
            {
                "id": 2,
                "name": "Addis Ababa - Piassa",
                "manager_name": "Selamawit Tadesse",
                "par": 9.8,
                "npl_ratio": 3.0,
                "portfolio": 2210000000,
                "accounts": 760,
                "recovery_rate": 52.4,
            },
            {
                "id": 3,
                "name": "Adama",
                "manager_name": "Getachew Alemu",
                "par": 11.6,
                "npl_ratio": 3.9,
                "portfolio": 1740000000,
                "accounts": 610,
                "recovery_rate": 46.8,
            },
            {
                "id": 4,
                "name": "Hawassa",
                "manager_name": "Meseret Wolde",
                "par": 10.9,
                "npl_ratio": 3.4,
                "portfolio": 1690000000,
                "accounts": 580,
                "recovery_rate": 48.2,
            },
            {
                "id": 5,
                "name": "Bahir Dar",
                "manager_name": "Yohannes Fikru",
                "par": 12.7,
                "npl_ratio": 4.3,
                "portfolio": 1420000000,
                "accounts": 520,
                "recovery_rate": 42.1,
            },
            {
                "id": 6,
                "name": "Dire Dawa",
                "manager_name": "Hana Bekele",
                "par": 11.3,
                "npl_ratio": 3.7,
                "portfolio": 1580000000,
                "accounts": 545,
                "recovery_rate": 45.7,
            },
        ],
        "total_portfolio": 11490000000,
        "average_par": 10.7,
        "average_recovery": 48.9,
    }


def get_branch_detail(branch_id: int) -> dict[str, Any]:
    """Get specific branch details."""
    _ = branch_id
    return {}


def get_branch_ranking() -> dict[str, Any]:
    """Get branch performance ranking."""
    return {
        "ranking": [
            {"rank": 1, "branch": "Addis Ababa - Bole", "par": 7.9, "recovery_rate": 58.1, "score": 91},
            {"rank": 2, "branch": "Addis Ababa - Piassa", "par": 9.8, "recovery_rate": 52.4, "score": 85},
            {"rank": 3, "branch": "Hawassa", "par": 10.9, "recovery_rate": 48.2, "score": 78},
            {"rank": 4, "branch": "Adama", "par": 11.6, "recovery_rate": 46.8, "score": 74},
            {"rank": 5, "branch": "Dire Dawa", "par": 11.3, "recovery_rate": 45.7, "score": 73},
            {"rank": 6, "branch": "Bahir Dar", "par": 12.7, "recovery_rate": 42.1, "score": 68},
        ]
    }
