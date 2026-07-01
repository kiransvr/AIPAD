"""Regional analytics business logic service."""
from __future__ import annotations

from hashlib import md5
from typing import Any

import pandas as pd

from src.services.upload_service import get_uploaded_dataframe


COUNTRY_CENTROIDS: dict[str, tuple[float, float]] = {
    "ethiopia": (9.145, 40.4897),
    "kenya": (-0.0236, 37.9062),
    "uganda": (1.3733, 32.2903),
    "rwanda": (-1.9403, 29.8739),
    "tanzania": (-6.369, 34.8888),
    "ghana": (7.9465, -1.0232),
    "nigeria": (9.082, 8.6753),
    "india": (20.5937, 78.9629),
    "pakistan": (30.3753, 69.3451),
    "bangladesh": (23.685, 90.3563),
    "nepal": (28.3949, 84.124),
    "usa": (39.7837, -100.4459),
    "united states": (39.7837, -100.4459),
    "canada": (61.0667, -107.9917),
    "brazil": (-10.3333, -53.2),
    "uk": (55.3781, -3.436),
    "united kingdom": (55.3781, -3.436),
}


def _get_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {column.lower(): column for column in df.columns}
    for candidate in candidates:
        found = lower_map.get(candidate.lower())
        if found:
            return found
    return None


def _risk_level(par_value: float) -> str:
    if par_value >= 12:
        return "high"
    if par_value >= 8:
        return "medium"
    return "low"


def _jitter(seed_text: str, max_offset: float = 1.2) -> tuple[float, float]:
    digest = md5(seed_text.encode("utf-8")).hexdigest()
    lat_seed = int(digest[:8], 16) / 0xFFFFFFFF
    lng_seed = int(digest[8:16], 16) / 0xFFFFFFFF
    lat_offset = (lat_seed - 0.5) * 2 * max_offset
    lng_offset = (lng_seed - 0.5) * 2 * max_offset
    return lat_offset, lng_offset


def _uploaded_map_data() -> dict[str, Any] | None:
    dataframe = get_uploaded_dataframe()
    if dataframe is None or dataframe.empty:
        return None

    branch_column = _get_column(dataframe, ["BranchName", "Branch", "Region", "RegionName"])
    if not branch_column:
        return None

    country_column = _get_column(dataframe, ["Country", "CountryName", "Nation"])
    age_column = _get_column(dataframe, ["AgeDays", "ArrearsDays", "DaysPastDue"])
    loan_amount_column = _get_column(dataframe, ["OutstandingBalance", "LoanAmount", "Balance"])
    latitude_column = _get_column(dataframe, ["Latitude", "Lat"])
    longitude_column = _get_column(dataframe, ["Longitude", "Lng", "Long"])

    df = dataframe.copy()
    df["__branch"] = df[branch_column].fillna("Unknown Branch").astype(str)
    df["__country"] = (
        df[country_column].fillna("Ethiopia").astype(str)
        if country_column
        else "Ethiopia"
    )
    df["__age"] = pd.to_numeric(df[age_column], errors="coerce").fillna(0) if age_column else 0
    df["__amount"] = (
        pd.to_numeric(df[loan_amount_column], errors="coerce").fillna(0)
        if loan_amount_column
        else 0
    )

    if latitude_column and longitude_column:
        df["__lat"] = pd.to_numeric(df[latitude_column], errors="coerce")
        df["__lng"] = pd.to_numeric(df[longitude_column], errors="coerce")
        grouped = df.dropna(subset=["__lat", "__lng"]).groupby(["__country", "__branch", "__lat", "__lng"], as_index=False)
    else:
        grouped = df.groupby(["__country", "__branch"], as_index=False)

    if grouped.ngroups == 0:
        return None

    points: list[dict[str, Any]] = []
    for _, group in grouped:
        accounts = int(len(group))
        par_ratio = float((group["__age"] >= 30).mean() * 100) if accounts > 0 else 0.0
        npl_ratio = float((group["__age"] >= 90).mean() * 100) if accounts > 0 else 0.0
        country_name = str(group["__country"].iloc[0])
        branch_name = str(group["__branch"].iloc[0])

        if "__lat" in group.columns and "__lng" in group.columns:
            lat = float(group["__lat"].iloc[0])
            lng = float(group["__lng"].iloc[0])
        else:
            base_lat, base_lng = COUNTRY_CENTROIDS.get(country_name.strip().lower(), (0.0, 0.0))
            lat_offset, lng_offset = _jitter(f"{country_name}:{branch_name}")
            lat = base_lat + lat_offset
            lng = base_lng + lng_offset

        points.append(
            {
                "name": branch_name,
                "country": country_name,
                "lat": round(lat, 4),
                "lng": round(lng, 4),
                "accounts": accounts,
                "portfolio": round(float(group["__amount"].sum()), 2),
                "par": round(par_ratio, 2),
                "npl_ratio": round(npl_ratio, 2),
                "risk_level": _risk_level(par_ratio),
            }
        )

    primary_country = max(
        (
            (country, int(count))
            for country, count in df["__country"].value_counts().items()
        ),
        key=lambda item: item[1],
        default=("Unknown", 0),
    )[0]

    return {
        "country": primary_country,
        "source": "uploaded",
        "point_count": len(points),
        "points": points,
    }


def get_risk_heatmap() -> dict[str, Any]:
    """Get regional risk heatmap data."""
    return {
        "regions": [
            {
                "name": "Addis Ababa",
                "par": 7.8,
                "npl_ratio": 2.4,
                "risk_level": "low",
                "accounts": 1860,
                "portfolio": 3250000000,
            },
            {
                "name": "Oromia",
                "par": 11.4,
                "npl_ratio": 3.5,
                "risk_level": "high",
                "accounts": 2410,
                "portfolio": 2980000000,
            },
            {
                "name": "Amhara",
                "par": 10.8,
                "npl_ratio": 3.2,
                "risk_level": "medium",
                "accounts": 1640,
                "portfolio": 2070000000,
            },
            {
                "name": "Sidama",
                "par": 9.7,
                "npl_ratio": 2.9,
                "risk_level": "medium",
                "accounts": 980,
                "portfolio": 1310000000,
            },
            {
                "name": "Tigray",
                "par": 13.1,
                "npl_ratio": 4.4,
                "risk_level": "high",
                "accounts": 870,
                "portfolio": 1040000000,
            },
            {
                "name": "Dire Dawa",
                "par": 10.2,
                "npl_ratio": 3.1,
                "risk_level": "medium",
                "accounts": 690,
                "portfolio": 920000000,
            },
        ]
    }


def get_risk_zones() -> dict[str, Any]:
    """Get risk zone classifications."""
    return {
        "zones": [
            {"zone": "Low Risk", "par_range": "0-8%", "regions": ["Addis Ababa"], "accounts": 1860},
            {
                "zone": "Medium Risk",
                "par_range": "8-12%",
                "regions": ["Amhara", "Sidama", "Dire Dawa"],
                "accounts": 3310,
            },
            {"zone": "High Risk", "par_range": "12%+", "regions": ["Oromia", "Tigray"], "accounts": 3280},
        ]
    }


def get_region_detail(region_id: str) -> dict[str, Any]:
    """Get specific region details."""
    _ = region_id
    return {}


def get_map_data() -> dict[str, Any]:
    """Get geospatial map points for regional plotting."""
    uploaded = _uploaded_map_data()
    if uploaded:
        return uploaded

    return {
        "country": "Ethiopia",
        "source": "fallback",
        "point_count": 6,
        "points": [
            {"name": "Addis Ababa", "country": "Ethiopia", "lat": 8.9806, "lng": 38.7578, "accounts": 1860, "portfolio": 3250000000, "par": 7.8, "npl_ratio": 2.4, "risk_level": "low"},
            {"name": "Oromia", "country": "Ethiopia", "lat": 8.7347, "lng": 39.2923, "accounts": 2410, "portfolio": 2980000000, "par": 11.4, "npl_ratio": 3.5, "risk_level": "high"},
            {"name": "Amhara", "country": "Ethiopia", "lat": 11.592, "lng": 37.3881, "accounts": 1640, "portfolio": 2070000000, "par": 10.8, "npl_ratio": 3.2, "risk_level": "medium"},
            {"name": "Sidama", "country": "Ethiopia", "lat": 6.957, "lng": 38.4764, "accounts": 980, "portfolio": 1310000000, "par": 9.7, "npl_ratio": 2.9, "risk_level": "medium"},
            {"name": "Tigray", "country": "Ethiopia", "lat": 13.4969, "lng": 39.4753, "accounts": 870, "portfolio": 1040000000, "par": 13.1, "npl_ratio": 4.4, "risk_level": "high"},
            {"name": "Dire Dawa", "country": "Ethiopia", "lat": 9.6009, "lng": 41.8501, "accounts": 690, "portfolio": 920000000, "par": 10.2, "npl_ratio": 3.1, "risk_level": "medium"},
        ],
    }
