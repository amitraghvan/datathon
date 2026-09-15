"""Unit and contract tests for Data Access Layer and UI business logic."""


from src.data_access.repository import (
    apply_dataframe_filters,
    get_all_schools_enriched,
    get_district_summary,
    get_electricity_comparison,
    get_procurement_summary,
    get_school_assessments,
    get_school_attendance_timeseries,
    get_school_profile,
    get_school_segmentation_data,
)
from src.ui.formatting import (
    format_gap,
    format_inr,
    format_kg,
    format_number,
    format_percent,
)


def test_get_all_schools_enriched_contract():
    """Verify enriched schools query contract."""
    df = get_all_schools_enriched()
    assert len(df) == 600
    expected_cols = [
        "school_id",
        "school_name",
        "district",
        "block",
        "enrollment",
        "attendance_rate",
        "academic_score",
        "infrastructure_readiness_pct",
        "risk_score",
        "risk_level",
        "primary_risk_driver",
        "intervention_priority_score",
        "intervention_rank",
        "welfare_quadrant",
    ]
    for col in expected_cols:
        assert col in df.columns

    # Verify bounds
    assert (df["attendance_rate"] >= 0.0).all()
    assert (df["attendance_rate"] <= 100.0).all()
    assert (df["intervention_priority_score"] >= 0.0).all()
    assert (df["intervention_priority_score"] <= 100.0).all()
    assert df["intervention_rank"].min() == 1
    assert df["intervention_rank"].max() == 600

def test_get_district_summary_contract():
    """Verify district summary query contract."""
    df = get_district_summary()
    assert len(df) > 0
    assert "district" in df.columns
    assert "avg_attendance_rate" in df.columns
    assert "district_risk_rate_pct" in df.columns
    assert df["school_count"].sum() == 600

def test_get_procurement_summary_contract():
    """Verify procurement summary query contract."""
    df = get_procurement_summary()
    assert len(df) == 600
    assert "avg_cost_per_student" in df.columns
    assert "avg_cost_per_kg" in df.columns
    assert "is_procurement_outlier" in df.columns
    assert (df["avg_cost_per_student"] >= 0.0).all()

def test_get_electricity_comparison_contract():
    """Verify electricity comparison returns valid status tiers and averages."""
    df = get_electricity_comparison()
    assert not df.empty
    assert "electricity_status" in df.columns
    assert "avg_academic_score" in df.columns
    assert set(df["electricity_status"]).issubset({"TRUE", "FALSE", "UNKNOWN"})

def test_school_profile_resolution():
    """Verify school profile resolves correctly for valid ID and gracefully for invalid ID."""
    prof = get_school_profile("SCH0001")
    assert prof is not None
    assert prof["school_id"] == "SCH0001"
    assert "enrollment" in prof
    assert "attendance_rate" in prof

    # Invalid school returns None gracefully
    prof_invalid = get_school_profile("NON_EXISTENT_ID")
    assert prof_invalid is None

def test_school_timeseries_and_assessments():
    """Verify single-school time series and assessment detail retrieval."""
    df_att = get_school_attendance_timeseries("SCH0001")
    assert not df_att.empty
    assert "attendance_rate" in df_att.columns
    assert "is_trusted_attendance" in df_att.columns

    df_acad = get_school_assessments("SCH0001")
    assert not df_acad.empty
    assert "subject_standard" in df_acad.columns
    assert "normalized_score_pct" in df_acad.columns

def test_school_segmentation_retrieval():
    """Verify K-Means segmentation data retrieval."""
    df_seg = get_school_segmentation_data()
    assert len(df_seg) == 600
    assert "cluster_id" in df_seg.columns
    assert "cluster_name" in df_seg.columns

def test_apply_dataframe_filters():
    """Verify filter logic handles subsets and empty scenarios correctly."""
    df = get_all_schools_enriched()

    # Filter by District
    filtered_amr = apply_dataframe_filters(df, {"district": "Amritsar"})
    assert (filtered_amr["district"] == "Amritsar").all()
    assert len(filtered_amr) < len(df)

    # Filter by Risk Level
    filtered_low = apply_dataframe_filters(df, {"risk_level": "LOW"})
    assert (filtered_low["risk_level"] == "LOW").all()

    # Filter by Welfare Quadrant
    filtered_quad = apply_dataframe_filters(df, {"welfare_quadrant": "MODEL"})
    assert (filtered_quad["welfare_quadrant"] == "MODEL").all()

    # Non-existent combination results in empty dataframe gracefully
    filtered_empty = apply_dataframe_filters(df, {"district": "Amritsar", "block": "NON_EXISTENT_BLOCK"})
    assert len(filtered_empty) == 0

def test_ui_formatting_helpers():
    """Verify formatting functions format valid values and handle None/NaN gracefully."""
    assert format_number(1234567) == "1,234,567"
    assert format_number(None) == "N/A"

    assert format_percent(84.567, 1) == "84.6%"
    assert format_percent(None) == "N/A"

    assert format_inr(1500) == "₹1,500"
    assert format_inr(150000, compact=True) == "₹1.50 L"
    assert format_inr(None) == "₹0"

    assert format_kg(5000) == "5,000 kg"
    assert format_kg(None) == "0 kg"

    assert format_gap(4.5) == "+4.5 pp"
    assert format_gap(-3.2) == "-3.2 pp"
    assert format_gap(0.0) == "0.0 pp"
    assert format_gap(None) == "0.0 pp"
