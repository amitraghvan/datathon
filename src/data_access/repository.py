"""Repository pattern implementation for EduPulse AI analytical data access.

Decouples all database queries, joins, and caching from UI presentation components.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from src.data_access.cache import cache_data_wrapper
from src.data_access.queries import (
    DATA_QUALITY_OVERVIEW_SQL,
    DISTRICT_SUMMARY_SQL,
    ELECTRICITY_IMPACT_ANALYSIS_SQL,
    PROCUREMENT_ENRICHED_SQL,
    SCHOOL_ASSESSMENT_DETAILS_SQL,
    SCHOOL_ATTENDANCE_SERIES_SQL,
    SCHOOL_MASTER_ENRICHED_SQL,
)
from src.modeling.database import get_db_connection


@cache_data_wrapper(show_spinner=False)
def get_all_schools_enriched() -> pd.DataFrame:
    """Fetch complete cohort of 600 schools joined across performance, welfare, risk, and priority."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(SCHOOL_MASTER_ENRICHED_SQL).df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_district_summary() -> pd.DataFrame:
    """Fetch rolled up district performance, risk rates, and quality coverage."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(DISTRICT_SUMMARY_SQL).df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_procurement_summary(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Fetch procurement transactions and IQR anomaly flags."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(PROCUREMENT_ENRICHED_SQL).df()
    finally:
        con.close()

    if filters:
        df = apply_dataframe_filters(df, filters)
    return df

@cache_data_wrapper(show_spinner=False)
def get_data_quality_summary() -> pd.DataFrame:
    """Fetch school-level data quality and trust audit matrix."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(DATA_QUALITY_OVERVIEW_SQL).df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_electricity_comparison() -> pd.DataFrame:
    """Compare academic performance and attendance across electricity availability tiers."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(ELECTRICITY_IMPACT_ANALYSIS_SQL).df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_school_profile(school_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full 360-degree operational profile for a single school."""
    df_all = get_all_schools_enriched()
    matched = df_all[df_all["school_id"] == school_id]
    if matched.empty:
        return None
    return matched.iloc[0].to_dict()

@cache_data_wrapper(show_spinner=False)
def get_school_attendance_timeseries(school_id: str) -> pd.DataFrame:
    """Fetch daily attendance observation history for a specific school."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(SCHOOL_ATTENDANCE_SERIES_SQL, [school_id]).df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_school_assessments(school_id: str) -> pd.DataFrame:
    """Fetch subject-level assessment details for a specific school."""
    con = get_db_connection(read_only=True)
    try:
        df = con.execute(SCHOOL_ASSESSMENT_DETAILS_SQL, [school_id]).df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_school_segmentation_data() -> pd.DataFrame:
    """Fetch K-Means empirical school segmentation clusters."""
    from src.config import PROCESSED_DATA_DIR
    p_path = PROCESSED_DATA_DIR / "school_segmentation.parquet"
    if p_path.exists():
        return pd.read_parquet(p_path)
    con = get_db_connection(read_only=True)
    try:
        df = con.execute("SELECT * FROM school_segmentation;").df()
    finally:
        con.close()
    return df

@cache_data_wrapper(show_spinner=False)
def get_dim_filters() -> Dict[str, List[str]]:
    """Fetch distinct dimension attributes for building cascading filter widgets."""
    df = get_all_schools_enriched()
    districts = sorted([d for d in df["district"].dropna().unique() if d != "Unknown"])
    if "Unknown" in df["district"].values:
        districts.append("Unknown")

    blocks = sorted(df["block"].dropna().unique().tolist())
    school_types = sorted(df["school_type"].dropna().unique().tolist())
    mediums = sorted(df["medium"].dropna().unique().tolist())
    risk_levels = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    drivers = ["INFRASTRUCTURE", "ACADEMIC", "ATTENDANCE", "MULTI_FACTOR"]
    welfare_quadrants = ["MODEL", "ACADEMIC INTERVENTION", "RESILIENT", "CRITICAL INTERVENTION"]

    return {
        "districts": districts,
        "blocks": blocks,
        "school_types": school_types,
        "mediums": mediums,
        "risk_levels": risk_levels,
        "drivers": drivers,
        "welfare_quadrants": welfare_quadrants,
    }

def apply_dataframe_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply dictionary of active user filters to a dataframe."""
    filtered = df.copy()

    if not filters:
        return filtered

    if filters.get("district") and filters["district"] != "All":
        filtered = filtered[filtered["district"] == filters["district"]]

    if filters.get("block") and filters["block"] != "All":
        filtered = filtered[filtered["block"] == filters["block"]]

    if filters.get("school_type") and filters["school_type"] != "All":
        filtered = filtered[filtered["school_type"] == filters["school_type"]]

    if filters.get("medium") and filters["medium"] != "All":
        filtered = filtered[filtered["medium"] == filters["medium"]]

    if filters.get("risk_level") and filters["risk_level"] != "All":
        if "risk_level" in filtered.columns:
            filtered = filtered[filtered["risk_level"] == filters["risk_level"]]

    if filters.get("primary_driver") and filters["primary_driver"] != "All":
        if "primary_risk_driver" in filtered.columns:
            filtered = filtered[filtered["primary_risk_driver"] == filters["primary_driver"]]

    if filters.get("welfare_quadrant") and filters["welfare_quadrant"] != "All":
        if "welfare_quadrant" in filtered.columns:
            filtered = filtered[filtered["welfare_quadrant"] == filters["welfare_quadrant"]]

    return filtered

def get_filtered_schools(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Fetch enriched schools filtered by active user criteria."""
    df = get_all_schools_enriched()
    if filters:
        df = apply_dataframe_filters(df, filters)
    return df
