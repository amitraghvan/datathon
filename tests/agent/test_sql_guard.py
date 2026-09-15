"""Unit tests for SQL Safety Guard and Injection Defense."""

import pytest

from src.agent.execution.sql_guard import (
    SecurityViolationError,
    SQLGuard,
    validate_sql_safety,
)


def test_valid_select_queries_pass():
    """Ensure standard SELECT and WITH queries pass safety checks."""
    assert validate_sql_safety("SELECT * FROM school_master_enriched LIMIT 10") is True
    assert validate_sql_safety("WITH cte AS (SELECT district, avg_attendance FROM district_performance) SELECT * FROM cte") is True
    assert SQLGuard.validate("SELECT school_id, intervention_priority_score FROM school_master_enriched WHERE district = 'Patiala'") is True


def test_disallowed_dml_and_ddl_blocked():
    """Verify write, modification, and schema alteration keywords are blocked."""
    unsafe_queries = [
        "DROP TABLE school_master_enriched",
        "DELETE FROM district_performance WHERE district = 'Amritsar'",
        "UPDATE school_master_enriched SET attendance_rate_pct = 100",
        "INSERT INTO school_master_enriched VALUES ('SCH9999')",
        "TRUNCATE TABLE procurement_summary",
        "ALTER TABLE dim_school ADD COLUMN test INT",
        "PRAGMA table_info('school_master')",
        "ATTACH 'database.db' AS db2",
    ]
    for q in unsafe_queries:
        with pytest.raises(SecurityViolationError):
            validate_sql_safety(q)


def test_sql_injection_patterns_blocked():
    """Verify comment exploitation, query chaining, and filesystem functions are blocked."""
    injections = [
        "SELECT * FROM schools; DROP TABLE students",
        "SELECT * FROM schools -- bypass check",
        "SELECT * FROM schools /* comment */ WHERE 1=1",
        "SELECT read_csv('data/raw/secret.csv')",
        "SELECT read_parquet('data/clean/passwords.parquet')",
    ]
    for q in injections:
        with pytest.raises(SecurityViolationError):
            validate_sql_safety(q)
