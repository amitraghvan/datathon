"""Student attendance cleaning, grade standardization, and anomaly detection engine.

Handles:
1. Grade normalization (Roman numerals 'I'-'X' and strings '1'-'10' -> integer).
2. Impossible attendance detection (present_students > total_students).
3. Proxy attendance fraud detection (100% attendance reported on Sundays).
4. Surrogate key synthesis for missing record_ids using deterministic MD5 hashes.
5. Teacher presence standardization.
6. Rigorous lineage and trusted record flags.
"""

import hashlib
from typing import Any, Tuple

import pandas as pd

from src.cleaning.booleans import normalize_boolean
from src.cleaning.dates import parse_date
from src.cleaning.ids import normalize_school_id
from src.config import GRADE_MAPPING


def normalize_grade(val: Any) -> Tuple[int | None, str]:
    """Normalize Roman or numeric grade to integer 1-10."""
    if pd.isna(val):
        return None, "MISSING_GRADE"
    s = str(val).strip().upper()
    if s in GRADE_MAPPING:
        return GRADE_MAPPING[s], "MAPPED_GRADE"
    if s.isdigit():
        return int(s), "NUMERIC_GRADE"
    return None, f"UNRECOGNIZED_GRADE: {s}"


def generate_attendance_surrogate_key(school_id: str, date_iso: str, grade: int) -> str:
    """Generate deterministic surrogate key for missing attendance record_ids."""
    payload = f"{school_id}_{date_iso}_{grade}"
    digest = hashlib.md5(payload.encode("utf-8")).hexdigest()[:8].upper()
    return f"ATT_{digest}"


def clean_attendance_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, list[dict]]:
    """Clean attendance dataframe, flag anomalies, and produce audit records.

    Returns:
        (df_cleaned, audit_entries)
    """
    audit_entries = []
    df = df_raw.copy()

    # 1. School ID normalization
    id_results = [normalize_school_id(x) for x in df["school_id"]]
    df["school_id_raw"] = df["school_id"]
    df["school_id"] = [r[0] for r in id_results]
    df["school_id_status"] = [r[1] for r in id_results]

    # 2. Date parsing & calendar features
    parsed_dates = [parse_date(d) for d in df["date"]]
    df["date_raw"] = df["date"]
    df["date"] = [p[0].isoformat() if p[0] else None for p in parsed_dates]
    df["day_of_week"] = [p[0].strftime("%A") if p[0] else None for p in parsed_dates]
    df["is_sunday"] = [p[0].weekday() == 6 if p[0] else False for p in parsed_dates]
    df["date_parse_status"] = [p[1] for p in parsed_dates]

    # 3. Grade normalization
    grade_res = [normalize_grade(g) for g in df["grade"]]
    df["grade_raw"] = df["grade"]
    df["grade_number"] = [g[0] for g in grade_res]

    # 4. Record ID surrogate resolution
    df["record_id_raw"] = df["record_id"]
    missing_id_mask = df["record_id"].isna() | (df["record_id"].astype(str).str.strip() == "")

    surrogates = []
    for idx, row in df.iterrows():
        if missing_id_mask[idx]:
            sid = row["school_id"] or "SCHXXXX"
            dt = row["date"] or "2025-01-01"
            gr = row["grade_number"] or 0
            surr_id = generate_attendance_surrogate_key(sid, dt, gr)
            surrogates.append(surr_id)
            audit_entries.append(
                {
                    "dataset": "track4_student_attendance.csv",
                    "record_id": surr_id,
                    "field_name": "record_id",
                    "raw_value": None,
                    "clean_value": surr_id,
                    "transformation": "SYNTHESIZE_SURROGATE_KEY",
                    "rule": "MD5(school_id + date + grade)[:8]",
                    "status": "RESCUED",
                    "quality_flag": "ATT_SURROGATE_KEY_GENERATED",
                    "reason": "Source record_id was missing or null.",
                }
            )
        else:
            surrogates.append(str(row["record_id"]).strip())

    df["record_id"] = surrogates

    # 5. Teacher present normalization
    tp_res = [normalize_boolean(x) for x in df["teacher_present"]]
    df["teacher_present_raw"] = df["teacher_present"]
    df["teacher_present_clean"] = [t[0] for t in tp_res]

    # 6. Marked by whitespace clean
    df["marked_by_raw"] = df["marked_by"]
    df["marked_by"] = df["marked_by"].fillna("Unknown").astype(str).str.strip()

    # 7. Student attendance validation & rate calculation
    df["total_students"] = (
        pd.to_numeric(df["total_students"], errors="coerce").fillna(0).astype(int)
    )
    df["present_students"] = (
        pd.to_numeric(df["present_students"], errors="coerce").fillna(0).astype(int)
    )

    # Calculate attendance rate
    # Prevent division by zero: if total_students <= 0, rate is null
    df["attendance_rate"] = [
        round((p / t) * 100.0, 2) if t > 0 else None
        for p, t in zip(df["present_students"], df["total_students"])
    ]

    # 8. Anomaly Detections:
    # A. Impossible attendance (present > total)
    df["is_impossible_attendance"] = df["present_students"] > df["total_students"]

    # B. Proxy attendance fraud (100% attendance on Sunday)
    df["is_proxy_attendance"] = (
        df["is_sunday"]
        & (df["present_students"] == df["total_students"])
        & (df["total_students"] > 0)
    )

    # 9. Quality status and trust classification
    quality_status = []
    anomaly_reasons = []
    is_trusted = []

    for idx, row in df.iterrows():
        reasons = []
        if row["is_impossible_attendance"]:
            reasons.append("PRESENT_STUDENTS_EXCEEDS_TOTAL")
            audit_entries.append(
                {
                    "dataset": "track4_student_attendance.csv",
                    "record_id": row["record_id"],
                    "field_name": "present_students",
                    "raw_value": row["present_students"],
                    "clean_value": row["present_students"],
                    "transformation": "FLAG_IMPOSSIBLE_RECORD",
                    "rule": "present_students <= total_students",
                    "status": "FLAGGED",
                    "quality_flag": "ERR_ATT_PRESENT_GT_TOTAL",
                    "reason": f"Present ({row['present_students']}) exceeds total ({row['total_students']}).",
                }
            )

        if row["is_proxy_attendance"]:
            reasons.append("100_PCT_ATTENDANCE_ON_SUNDAY")
            audit_entries.append(
                {
                    "dataset": "track4_student_attendance.csv",
                    "record_id": row["record_id"],
                    "field_name": "date / present_students",
                    "raw_value": f"{row['present_students']}/{row['total_students']}",
                    "clean_value": f"{row['present_students']}/{row['total_students']}",
                    "transformation": "FLAG_PROXY_FRAUD",
                    "rule": "100% attendance on Sunday",
                    "status": "FLAGGED",
                    "quality_flag": "WARN_ATT_SUNDAY_PROXY",
                    "reason": f"Sunday attendance recorded as exactly 100% ({row['present_students']}/{row['total_students']}).",
                }
            )

        if reasons:
            anomaly_reasons.append("; ".join(reasons))
            quality_status.append("FLAGGED_ANOMALY")
            is_trusted.append(False)
        else:
            anomaly_reasons.append(None)
            quality_status.append("VALID")
            is_trusted.append(True)

    df["quality_status"] = quality_status
    df["attendance_anomaly_reason"] = anomaly_reasons
    df["is_trusted_attendance"] = is_trusted

    # Select and order final canonical columns
    final_cols = [
        "record_id",
        "record_id_raw",
        "school_id",
        "school_id_raw",
        "date",
        "date_raw",
        "day_of_week",
        "is_sunday",
        "grade_number",
        "grade_raw",
        "total_students",
        "present_students",
        "attendance_rate",
        "teacher_present_clean",
        "teacher_present_raw",
        "marked_by",
        "is_impossible_attendance",
        "is_proxy_attendance",
        "is_trusted_attendance",
        "quality_status",
        "attendance_anomaly_reason",
    ]

    return df[final_cols], audit_entries
