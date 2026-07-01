"""Upload service for portfolio file ingestion and cached dataset access."""
from pathlib import Path
from typing import Any
import json
import tempfile

import pandas as pd
from fastapi import HTTPException, UploadFile

# Store uploaded data in memory (in production, this would be a database)
uploaded_data: dict[str, Any] = {
    "loans": [],
    "summary": {},
    "dataframe": None,
}

UPLOAD_DIR = Path(tempfile.gettempdir()) / "portfolio_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
LATEST_UPLOAD_META = UPLOAD_DIR / "latest_upload.json"

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def validate_file(filename: str) -> bool:
    """Validate file extension."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def process_excel_file(file_path: Path) -> pd.DataFrame:
    """Process Excel file and return DataFrame."""
    try:
        return pd.read_excel(file_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(exc)}") from exc


def process_csv_file(file_path: Path) -> pd.DataFrame:
    """Process CSV file and return DataFrame."""
    try:
        return pd.read_csv(file_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV file: {str(exc)}") from exc


def validate_loan_data(df: pd.DataFrame) -> dict[str, Any]:
    """Validate loan data and generate summary statistics."""
    required_columns = [
        "AccountNo",
        "AccountName",
        "BranchName",
        "LoanAmount",
        "OutstandingBalance",
        "AgeDays",
        "DefaultedInst",
    ]

    # Check for required columns (case-insensitive)
    df_columns_lower = {col.lower(): col for col in df.columns}
    required_lower = {col.lower() for col in required_columns}

    missing_columns = required_lower - set(df_columns_lower.keys())

    if missing_columns:
        return {
            "valid": False,
            "error": f"Missing required columns: {', '.join(missing_columns)}",
            "expected_columns": required_columns,
            "found_columns": list(df.columns),
        }

    try:
        total_accounts = len(df)
        total_portfolio = df["LoanAmount"].sum() if "LoanAmount" in df.columns else 0

        # PAR is accounts with 30+ days arrears.
        par_accounts = len(df[df.get("AgeDays", 0) >= 30]) if "AgeDays" in df.columns else 0
        par_ratio = (par_accounts / total_accounts * 100) if total_accounts > 0 else 0

        # NPL is accounts with 90+ days arrears.
        npl_accounts = len(df[df.get("AgeDays", 0) >= 90]) if "AgeDays" in df.columns else 0
        npl_ratio = (npl_accounts / total_accounts * 100) if total_accounts > 0 else 0

        return {
            "valid": True,
            "total_accounts": int(total_accounts),
            "total_portfolio": float(total_portfolio),
            "par_accounts": int(par_accounts),
            "par_ratio": round(float(par_ratio), 2),
            "npl_accounts": int(npl_accounts),
            "npl_ratio": round(float(npl_ratio), 2),
            "rows_processed": int(total_accounts),
        }
    except Exception as exc:
        return {
            "valid": False,
            "error": f"Error processing data: {str(exc)}",
        }


def get_uploaded_dataframe() -> pd.DataFrame | None:
    """Return the latest uploaded dataframe if one exists."""
    dataframe = uploaded_data.get("dataframe")
    if isinstance(dataframe, pd.DataFrame):
        return dataframe

    persisted_path = None
    if LATEST_UPLOAD_META.exists():
        try:
            with LATEST_UPLOAD_META.open("r", encoding="utf-8") as file_obj:
                persisted = json.load(file_obj)
            candidate = persisted.get("file_path")
            if candidate:
                candidate_path = Path(candidate)
                if candidate_path.exists():
                    persisted_path = candidate_path
        except Exception:
            persisted_path = None

    if persisted_path is None:
        candidates = [
            path
            for path in UPLOAD_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
        ]
        if candidates:
            persisted_path = max(candidates, key=lambda item: item.stat().st_mtime)

    if persisted_path is None:
        return None

    try:
        file_ext = persisted_path.suffix.lower()
        if file_ext in [".xlsx", ".xls"]:
            dataframe = pd.read_excel(persisted_path)
        else:
            dataframe = pd.read_csv(persisted_path)
        uploaded_data["dataframe"] = dataframe
        uploaded_data["loans"] = dataframe.to_dict("records")[:1000]
        if not uploaded_data.get("summary"):
            uploaded_data["summary"] = validate_loan_data(dataframe)
        return dataframe
    except Exception:
        return None


def get_uploaded_summary() -> dict[str, Any]:
    """Return the latest upload summary."""
    summary = uploaded_data.get("summary", {})
    if summary:
        return summary

    dataframe = get_uploaded_dataframe()
    if dataframe is None:
        return {}

    summary = validate_loan_data(dataframe)
    uploaded_data["summary"] = summary
    return summary


async def upload_portfolio_data(
    file: UploadFile,
    uploader_username: str | None = None,
    uploader_role: str | None = None,
) -> dict[str, Any]:
    """Upload and validate a portfolio file (Excel/CSV)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not validate_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        file_path = UPLOAD_DIR / file.filename
        contents = await file.read()

        with open(file_path, "wb") as file_obj:
            file_obj.write(contents)

        file_ext = Path(file.filename).suffix.lower()
        if file_ext in [".xlsx", ".xls"]:
            dataframe = process_excel_file(file_path)
        else:
            dataframe = process_csv_file(file_path)

        validation_result = validate_loan_data(dataframe)

        if not validation_result.get("valid"):
            return {
                "status": "error",
                "filename": file.filename,
                "file_size": len(contents),
                "error": validation_result.get("error"),
                "details": validation_result,
            }

        uploaded_data["loans"] = dataframe.to_dict("records")[:1000]
        uploaded_data["dataframe"] = dataframe.copy()
        uploaded_data["summary"] = {
            "upload_date": pd.Timestamp.now().isoformat(),
            "filename": file.filename,
            "file_size_bytes": len(contents),
            "uploaded_by": uploader_username or "unknown",
            "uploader_role": uploader_role or "unknown",
            **validation_result,
        }

        try:
            with LATEST_UPLOAD_META.open("w", encoding="utf-8") as file_obj:
                json.dump(
                    {
                        "file_path": str(file_path),
                        "filename": file.filename,
                        "upload_date": pd.Timestamp.now().isoformat(),
                        "uploaded_by": uploader_username or "unknown",
                        "uploader_role": uploader_role or "unknown",
                    },
                    file_obj,
                )
        except Exception:
            pass

        return {
            "status": "success",
            "message": f"Successfully uploaded {file.filename}",
            "filename": file.filename,
            "file_size_bytes": len(contents),
            "summary": uploaded_data["summary"],
            "upload_id": file_path.stem,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(exc)}") from exc


def get_upload_status() -> dict[str, Any]:
    """Get status of last uploaded data."""
    summary = get_uploaded_summary()
    if not summary:
        return {
            "status": "no_data",
            "message": "No data has been uploaded yet",
        }

    return {
        "status": "success",
        "data": summary,
        "records_stored": len(uploaded_data["loans"]),
    }


def get_sample_template() -> dict[str, Any]:
    """Get sample data template for portfolio upload."""
    return {
        "template": {
            "AccountNo": "452150010",
            "AccountName": "John Doe",
            "BranchName": "Addis Ababa - Bole",
            "LoanAmount": 100000,
            "OutstandingBalance": 45000,
            "AgeDays": 15,
            "DefaultedInst": 0,
            "Officer": "Abebe Kebede",
            "LoanProduct": "Working Capital",
            "Gender": "M",
            "Sector": "Agriculture",
        },
        "instructions": [
            "Download this template as Excel or CSV",
            "Fill in your loan portfolio data",
            "Required columns: AccountNo, AccountName, BranchName, LoanAmount, OutstandingBalance, AgeDays, DefaultedInst",
            "Optional columns: Officer, LoanProduct, Gender, Sector",
            "Upload back to /api/v1/upload endpoint",
            "System will validate and generate analytics",
        ],
        "field_descriptions": {
            "AccountNo": "Unique loan account identifier",
            "AccountName": "Borrower name",
            "BranchName": "Branch where loan was disbursed",
            "LoanAmount": "Original loan amount in ETB",
            "OutstandingBalance": "Current unpaid balance in ETB",
            "AgeDays": "Days since last payment (arrears days)",
            "DefaultedInst": "Number of defaulted installments",
            "Officer": "Loan officer assigned (optional)",
            "LoanProduct": "Type of loan product (optional)",
            "Gender": "Borrower gender M/F/Other (optional)",
            "Sector": "Economic sector (optional)",
        },
    }


def reset_uploaded_data() -> dict[str, str]:
    """Reset uploaded data cache and latest-pointer metadata."""
    global uploaded_data
    uploaded_data = {
        "loans": [],
        "summary": {},
        "dataframe": None,
    }

    if LATEST_UPLOAD_META.exists():
        LATEST_UPLOAD_META.unlink()

    return {
        "status": "success",
        "message": "Uploaded data has been reset",
    }
