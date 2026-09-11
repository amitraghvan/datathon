"""Unit tests for attendance cleaning and anomaly detection."""

import pandas as pd
import pytest
from src.cleaning.attendance import (
    normalize_grade,
    generate_attendance_surrogate_key,
    clean_attendance_data,
)

def test_normalize_grade():
    assert normalize_grade("I")[0] == 1
    assert normalize_grade("V")[0] == 5
    assert normalize_grade("5")[0] == 5
    assert normalize_grade("10")[0] == 10
    assert normalize_grade("X")[0] == 10
    assert normalize_grade(None)[0] is None

def test_generate_attendance_surrogate_key():
    k1 = generate_attendance_surrogate_key("SCH0050", "2025-05-15", 5)
    k2 = generate_attendance_surrogate_key("SCH0050", "2025-05-15", 5)
    assert k1.startswith("ATT_")
    assert k1 == k2  # Deterministic!

def test_clean_attendance_data_impossible_attendance():
    # Present (110) > Total (100)
    raw_df = pd.DataFrame([{
        "record_id": "ATT999001",
        "date": "2025-05-15", # Thursday
        "school_id": "SCH-0050",
        "grade": "V",
        "total_students": 100,
        "present_students": 110,
        "teacher_present": "True",
        "marked_by": "Headmaster",
    }])

    df_clean, audit = clean_attendance_data(raw_df)
    row = df_clean.iloc[0]
    assert bool(row["is_impossible_attendance"]) is True
    assert bool(row["is_trusted_attendance"]) is False
    assert row["quality_status"] == "FLAGGED_ANOMALY"
    assert "PRESENT_STUDENTS_EXCEEDS_TOTAL" in row["attendance_anomaly_reason"]
    # Student counts must not be altered
    assert row["present_students"] == 110
    assert row["total_students"] == 100

def test_clean_attendance_data_proxy_attendance_sunday():
    # 2025-05-04 is a Sunday
    raw_df = pd.DataFrame([{
        "record_id": "ATT999002",
        "date": "2025-05-04",
        "school_id": "SCH0050",
        "grade": "5",
        "total_students": 80,
        "present_students": 80, # 100% on Sunday
        "teacher_present": "haan",
        "marked_by": "Class Teacher",
    }])

    df_clean, audit = clean_attendance_data(raw_df)
    row = df_clean.iloc[0]
    assert bool(row["is_sunday"]) is True
    assert bool(row["is_proxy_attendance"]) is True
    assert bool(row["is_trusted_attendance"]) is False
    assert row["attendance_rate"] == 100.0

def test_clean_attendance_missing_record_id_surrogate():
    raw_df = pd.DataFrame([{
        "record_id": None,
        "date": "2025-05-15",
        "school_id": "SCH0050",
        "grade": "5",
        "total_students": 50,
        "present_students": 45,
        "teacher_present": "1",
        "marked_by": "Clerk",
    }])

    df_clean, audit = clean_attendance_data(raw_df)
    row = df_clean.iloc[0]
    assert row["record_id"].startswith("ATT_")
    assert any(a["transformation"] == "SYNTHESIZE_SURROGATE_KEY" for a in audit)
