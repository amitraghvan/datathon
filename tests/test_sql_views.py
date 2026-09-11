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
    for col in ["electricity_status", "water_status", "toilet_status", "boundary_status", "playground_status"]:
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
