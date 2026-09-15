"""Unit and integration tests for analytical SQL views."""

import pytest

from src.modeling.database import get_db_connection


@pytest.fixture(scope="module")
def db_conn():
    """Acquire read-only connection."""
    con = get_db_connection(read_only=True)
    yield con
    con.close()


def test_view_school_performance(db_conn):
    """Verify school_performance view schema, count, and weighted metrics."""
    df = db_conn.execute("SELECT * FROM school_performance").df()
    assert len(df) == 600
    assert "attendance_rate" in df.columns
    assert "academic_score" in df.columns
    assert "quality_coverage_pct" in df.columns

    # Verify rates are bounded 0-100
    assert (df["attendance_rate"] >= 0.0).all()
    assert (df["attendance_rate"] <= 100.0).all()
    assert (df["academic_score"] >= 0.0).all()
    assert (df["academic_score"] <= 100.0).all()


def test_view_school_welfare(db_conn):
    """Verify school_welfare view infrastructure readiness scores."""
    df = db_conn.execute("SELECT * FROM school_welfare").df()
    assert len(df) == 600
    assert "infrastructure_readiness_pct" in df.columns
    assert (df["infrastructure_readiness_pct"] >= 0.0).all()
    assert (df["infrastructure_readiness_pct"] <= 100.0).all()

    # Verify standard values
    for col in [
        "electricity_status",
        "water_status",
        "toilet_status",
        "boundary_status",
        "playground_status",
    ]:
        assert set(df[col].unique()).issubset({"TRUE", "FALSE", "UNKNOWN"})


def test_view_district_performance(db_conn):
    """Verify district_performance roll-up integrity."""
    df = db_conn.execute("SELECT * FROM district_performance").df()
    assert len(df) > 0
    # Sum of schools across districts must equal 600
    assert df["school_count"].sum() == 600
    assert (df["avg_attendance_rate"] > 0).all()
    assert (df["avg_academic_score"] > 0).all()


def test_view_procurement_summary(db_conn):
    """Verify procurement_summary metrics and division by zero safety."""
    df = db_conn.execute("SELECT * FROM procurement_summary").df()
    assert len(df) == 600
    assert (df["total_quantity_kg"] >= 0.0).all()
    assert (df["total_spend_inr"] >= 0.0).all()
    # Check that average cost per kg is within realistic commodity bounds (between 25 and 125 INR/kg)
    valid_costs = df[df["total_quantity_kg"] > 0]["avg_cost_per_kg"]
    assert (valid_costs >= 25.0).all()
    assert (valid_costs <= 125.0).all()


def test_view_school_data_quality(db_conn):
    """Verify school_data_quality view completeness."""
    df = db_conn.execute("SELECT * FROM school_data_quality").df()
    assert len(df) == 600
    assert (df["total_operational_records"] > 0).all()
    assert (df["trusted_records"] > 0).all()
    assert (df["data_quality_rate_pct"] >= 0.0).all()
    assert (df["data_quality_rate_pct"] <= 100.0).all()


def test_view_school_risk(db_conn):
    """Verify school_risk view schema, bounds, and risk bands."""
    df = db_conn.execute("SELECT * FROM school_risk").df()
    assert len(df) == 600
    assert "risk_score" in df.columns
    assert "risk_level" in df.columns
    assert (df["risk_score"] >= 0.0).all()
    assert (df["risk_score"] <= 100.0).all()
    assert set(df["risk_level"].unique()).issubset({"LOW", "MODERATE", "HIGH", "CRITICAL"})


def test_view_school_intervention_priority(db_conn):
    """Verify school_intervention_priority view deterministic ranking."""
    df = db_conn.execute("SELECT * FROM school_intervention_priority").df()
    assert len(df) == 600
    assert "intervention_priority_score" in df.columns
    assert "intervention_rank" in df.columns
    assert (df["intervention_priority_score"] >= 0.0).all()
    assert (df["intervention_priority_score"] <= 100.0).all()
    assert df["intervention_rank"].tolist() == list(range(1, 601))


def test_view_school_welfare_gap(db_conn):
    """Verify school_welfare_gap 2x2 matrix distribution."""
    df = db_conn.execute("SELECT * FROM school_welfare_gap").df()
    assert len(df) == 600
    expected_quads = {"MODEL", "RESILIENT", "ACADEMIC INTERVENTION", "CRITICAL INTERVENTION"}
    assert set(df["welfare_quadrant"].unique()).issubset(expected_quads)


def test_view_district_risk_summary(db_conn):
    """Verify district_risk_summary aggregations."""
    df = db_conn.execute("SELECT * FROM district_risk_summary").df()
    assert len(df) > 0
    assert df["school_count"].sum() == 600
    assert (df["avg_risk_score"] >= 0.0).all()
    assert (df["district_risk_rate_pct"] >= 0.0).all()


def test_view_procurement_anomalies(db_conn):
    """Verify procurement_anomalies view outlier detection."""
    df = db_conn.execute("SELECT * FROM procurement_anomalies").df()
    assert len(df) == 600
    assert "is_procurement_outlier" in df.columns
    assert "procurement_anomaly_reason" in df.columns
