"""Unit and integration tests for the DuckDB canonical dimensional warehouse model."""

import pytest

from src.modeling.build_database import build_canonical_database
from src.modeling.database import get_db_connection


@pytest.fixture(scope="module")
def db_conn():
    """Ensure database is built and return read-only connection."""
    build_canonical_database()
    con = get_db_connection(read_only=True)
    yield con
    con.close()


def test_dimensions_primary_key_uniqueness(db_conn):
    """Verify primary key uniqueness across all dimensions."""
    dims = [
        ("dim_school", "school_key", "school_id"),
        ("dim_date", "date_key", "date"),
        ("dim_grade", "grade_key", "grade_number"),
        ("dim_subject", "subject_key", "subject_standard"),
        ("dim_vendor", "vendor_key", "vendor_id"),
        ("dim_grain", "grain_key", "grain_standard"),
    ]

    for table, pk_col, business_key in dims:
        counts = db_conn.execute(
            f"SELECT COUNT(*), COUNT(DISTINCT {pk_col}), COUNT(DISTINCT {business_key}) FROM {table}"
        ).fetchone()
        assert counts[0] == counts[1], f"Primary key {pk_col} not unique in {table}"
        assert counts[0] == counts[2], f"Business key {business_key} not unique in {table}"


def test_fact_foreign_key_referential_integrity(db_conn):
    """Verify zero orphaned foreign keys in any fact table."""
    orphans_att = db_conn.execute("""
        SELECT COUNT(*) FROM fact_attendance f
        LEFT JOIN dim_school s ON f.school_key = s.school_key
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        LEFT JOIN dim_grade g ON f.grade_key = g.grade_key
        WHERE s.school_key IS NULL OR d.date_key IS NULL OR g.grade_key IS NULL
    """).fetchone()[0]
    assert orphans_att == 0, f"Found {orphans_att} orphaned keys in fact_attendance"

    orphans_ass = db_conn.execute("""
        SELECT COUNT(*) FROM fact_assessment f
        LEFT JOIN dim_school s ON f.school_key = s.school_key
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        LEFT JOIN dim_grade g ON f.grade_key = g.grade_key
        LEFT JOIN dim_subject sub ON f.subject_key = sub.subject_key
        WHERE s.school_key IS NULL OR d.date_key IS NULL OR g.grade_key IS NULL OR sub.subject_key IS NULL
    """).fetchone()[0]
    assert orphans_ass == 0, f"Found {orphans_ass} orphaned keys in fact_assessment"

    orphans_inf = db_conn.execute("""
        SELECT COUNT(*) FROM fact_infrastructure f
        LEFT JOIN dim_school s ON f.school_key = s.school_key
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        WHERE s.school_key IS NULL OR d.date_key IS NULL
    """).fetchone()[0]
    assert orphans_inf == 0, f"Found {orphans_inf} orphaned keys in fact_infrastructure"

    orphans_pro = db_conn.execute("""
        SELECT COUNT(*) FROM fact_procurement f
        LEFT JOIN dim_school s ON f.school_key = s.school_key
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        LEFT JOIN dim_vendor v ON f.vendor_key = v.vendor_key
        LEFT JOIN dim_grain gr ON f.grain_key = gr.grain_key
        WHERE s.school_key IS NULL OR d.date_key IS NULL OR v.vendor_key IS NULL OR gr.grain_key IS NULL
    """).fetchone()[0]
    assert orphans_pro == 0, f"Found {orphans_pro} orphaned keys in fact_procurement"


def test_golden_value_ranges(db_conn):
    """Verify numerical boundaries and data consistency."""
    # 1. Normalized scores between 0 and 100
    score_stats = db_conn.execute("""
        SELECT MIN(normalized_score_pct), MAX(normalized_score_pct)
        FROM fact_assessment
        WHERE quality_status = 'VALID'
    """).fetchone()
    assert score_stats[0] >= 0.0
    assert score_stats[1] <= 100.0

    # 2. Trusted attendance rates between 0 and 100
    att_stats = db_conn.execute("""
        SELECT MIN(attendance_rate), MAX(attendance_rate)
        FROM fact_attendance
        WHERE is_trusted_attendance = TRUE
    """).fetchone()
    assert att_stats[0] >= 0.0
    assert att_stats[1] <= 100.0

    # 3. Procurement positive quantities and costs
    proc_stats = db_conn.execute("""
        SELECT MIN(quantity_kg), MIN(total_cost)
        FROM fact_procurement
        WHERE quality_status = 'VALID'
    """).fetchone()
    assert proc_stats[0] > 0.0
    assert proc_stats[1] > 0.0
