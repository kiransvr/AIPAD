"""Upload validation unit tests."""

import pandas as pd

from src.services.upload_service import validate_loan_data


def _valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "AccountNo": "A-1001",
                "AccountName": "Jane Doe",
                "BranchName": "Bole",
                "LoanAmount": 100000,
                "OutstandingBalance": 45000,
                "AgeDays": 25,
                "DefaultedInst": 0,
            },
            {
                "AccountNo": "A-1002",
                "AccountName": "John Doe",
                "BranchName": "Piassa",
                "LoanAmount": 80000,
                "OutstandingBalance": 30000,
                "AgeDays": 95,
                "DefaultedInst": 2,
            },
        ]
    )


def test_validate_loan_data_valid_dataframe_returns_summary() -> None:
    summary, normalized = validate_loan_data(_valid_dataframe())

    assert summary["valid"] is True
    assert summary["rows_processed"] == 2
    assert summary["error_count"] == 0
    assert isinstance(normalized, pd.DataFrame)
    assert list(normalized.columns)[:7] == [
        "AccountNo",
        "AccountName",
        "BranchName",
        "LoanAmount",
        "OutstandingBalance",
        "AgeDays",
        "DefaultedInst",
    ]


def test_validate_loan_data_reports_row_level_errors() -> None:
    invalid_df = pd.DataFrame(
        [
            {
                "AccountNo": "A-1003",
                "AccountName": "",
                "BranchName": "Bole",
                "LoanAmount": "abc",
                "OutstandingBalance": 9000,
                "AgeDays": -5,
                "DefaultedInst": 1.5,
            },
            {
                "AccountNo": "A-1004",
                "AccountName": "Sam",
                "BranchName": "",
                "LoanAmount": 10000,
                "OutstandingBalance": 15000,
                "AgeDays": 10,
                "DefaultedInst": 0,
            },
        ]
    )

    summary, normalized = validate_loan_data(invalid_df)

    assert summary["valid"] is False
    assert summary["error_count"] >= 4
    assert isinstance(summary.get("row_errors"), list)
    assert len(summary["row_errors"]) >= 4
    assert normalized is None


def test_validate_loan_data_missing_required_columns() -> None:
    missing_df = pd.DataFrame(
        [
            {
                "AccountNo": "A-1005",
                "AccountName": "Alex",
            }
        ]
    )

    summary, normalized = validate_loan_data(missing_df)

    assert summary["valid"] is False
    assert "Missing required columns" in summary["error"]
    assert "BranchName" in summary["expected_columns"]
    assert normalized is None
