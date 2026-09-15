"""Unit tests for the Retention & Intervention Risk Engine."""

from src.analytics.risk import (
    calculate_school_risk,
    classify_risk_level,
    get_recommended_intervention,
)


def test_classify_risk_level():
    assert classify_risk_level(15.0) == "LOW"
    assert classify_risk_level(35.0) == "MODERATE"
    assert classify_risk_level(65.0) == "HIGH"
    assert classify_risk_level(85.0) == "CRITICAL"
    assert classify_risk_level(100.0) == "CRITICAL"
    assert classify_risk_level(None) == "UNKNOWN"


def test_recommended_intervention_mapping():
    act_crit_multi = get_recommended_intervention("CRITICAL", "MULTI_FACTOR")
    assert "multi-factor" in act_crit_multi.lower()

    act_crit_att = get_recommended_intervention("CRITICAL", "ATTENDANCE")
    assert "attendance" in act_crit_att.lower()

    act_mod = get_recommended_intervention("MODERATE", "ATTENDANCE")
    assert "preventative" in act_mod.lower()

    act_low = get_recommended_intervention("LOW", "ATTENDANCE")
    assert "routine" in act_low.lower()


def test_calculate_school_risk_ranges_and_completeness():
    df_risk = calculate_school_risk()
    assert len(df_risk) == 600

    # Ensure risk score bounds
    valid_scores = df_risk[df_risk["risk_score"].notna()]["risk_score"]
    assert (valid_scores >= 0.0).all()
    assert (valid_scores <= 100.0).all()

    # Ensure priority score bounds
    assert (df_risk["intervention_priority_score"] >= 0.0).all()
    assert (df_risk["intervention_priority_score"] <= 100.0).all()

    # Verify deterministic rank: 1 to 600
    assert df_risk["intervention_rank"].tolist() == list(range(1, 601))

    # Verify allowed driver taxonomy
    allowed_drivers = {
        "ATTENDANCE",
        "ACADEMIC",
        "INFRASTRUCTURE",
        "MULTI_FACTOR",
        "DATA_INSUFFICIENT",
    }
    assert set(df_risk["primary_risk_driver"].unique()).issubset(allowed_drivers)

    # Verify coverage bounds
    assert (df_risk["risk_data_coverage_pct"] >= 0.0).all()
    assert (df_risk["risk_data_coverage_pct"] <= 100.0).all()


def test_risk_weighted_formula_and_dynamic_renormalization():
    df_risk = calculate_school_risk()
    # Check a sample of complete records
    complete = df_risk[
        df_risk["attendance_risk"].notna()
        & df_risk["academic_risk"].notna()
        & df_risk["infrastructure_risk"].notna()
    ]
    for _, row in complete.head(20).iterrows():
        expected = round(
            0.45 * row["attendance_risk"]
            + 0.35 * row["academic_risk"]
            + 0.20 * row["infrastructure_risk"],
            1,
        )
        assert abs(row["risk_score"] - expected) <= 0.1


def test_benchmark_gaps_and_amenity_counts():
    df_risk = calculate_school_risk()
    # Check amenity counts sum to 5 for every school
    assert (df_risk["known_amenity_count"] + df_risk["unknown_amenity_count"] == 5).all()
    # Check benchmark gaps are within reasonable percentage point ranges (-100 to +100)
    for gap_col in [
        "attendance_gap_vs_district",
        "academic_gap_vs_district",
        "infrastructure_gap_vs_district",
    ]:
        assert (df_risk[gap_col] >= -100.0).all()
        assert (df_risk[gap_col] <= 100.0).all()
