"""Unit tests for statistical association, welfare gap matrix, and sensitivity analyses."""

from src.analytics.advanced import (
    analyze_attendance_academic_association,
    calculate_welfare_gap_matrix,
    detect_procurement_outliers,
    run_letter_grade_sensitivity_analysis,
    run_risk_weight_sensitivity_analysis,
)


def test_attendance_academic_association():
    res = analyze_attendance_academic_association()
    assert res["sample_size"] == 600
    assert -1.0 <= res["pearson_r"] <= 1.0
    assert -1.0 <= res["spearman_rho"] <= 1.0
    assert res["association_strength"] in ("STRONG", "MODERATE", "WEAK", "NEGLIGIBLE")
    assert "causal" in res["narrative"].lower()  # Verifies explicit disclaimer is present!


def test_welfare_gap_matrix():
    df_quad = calculate_welfare_gap_matrix()
    assert len(df_quad) == 600
    expected_quads = {
        "MODEL",
        "RESILIENT",
        "ACADEMIC INTERVENTION",
        "CRITICAL INTERVENTION",
        "UNCLASSIFIED",
    }
    assert set(df_quad["welfare_quadrant"].unique()).issubset(expected_quads)
    # Check that counts across quadrants sum to 600
    assert df_quad["welfare_quadrant"].value_counts().sum() == 600


def test_risk_weight_sensitivity_analysis():
    sens = run_risk_weight_sensitivity_analysis()
    assert sens["overall_stability"] in ("ROBUST", "SENSITIVE")
    assert "Baseline (45/35/20)" in sens["scenario_evaluations"]
    for sc, metrics in sens["scenario_evaluations"].items():
        assert 0 <= metrics["top10_overlap_count"] <= 10
        assert metrics["rank_correlation_with_baseline"] >= 0.85


def test_letter_grade_sensitivity_analysis():
    res = run_letter_grade_sensitivity_analysis()
    assert res["sample_size"] == 600
    assert res["pearson_correlation"] >= 0.85
    assert res["district_pearson_correlation"] >= 0.95
    assert res["mean_risk_score_impact"] < 2.0
    assert res["is_stable"] is True


def test_procurement_outliers():
    df_outliers = detect_procurement_outliers()
    assert len(df_outliers) == 600
    assert "is_procurement_outlier" in df_outliers.columns
    assert (
        "fraud" not in " ".join(df_outliers["procurement_anomaly_reason"]).lower()
    )  # Never falsely claims fraud
