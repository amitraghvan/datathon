"""Data access layer package."""

from .repository import (
    apply_dataframe_filters,
    get_all_schools_enriched,
    get_data_quality_summary,
    get_dim_filters,
    get_district_summary,
    get_electricity_comparison,
    get_filtered_schools,
    get_procurement_summary,
    get_school_assessments,
    get_school_attendance_timeseries,
    get_school_profile,
    get_school_segmentation_data,
)

__all__ = [
    "get_all_schools_enriched",
    "get_filtered_schools",
    "get_district_summary",
    "get_procurement_summary",
    "get_data_quality_summary",
    "get_electricity_comparison",
    "get_school_profile",
    "get_school_attendance_timeseries",
    "get_school_assessments",
    "get_school_segmentation_data",
    "get_dim_filters",
    "apply_dataframe_filters",
]
