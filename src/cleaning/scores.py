"""Academic score normalization and subject standardization engine.

Supports six observed grading scales:
1. Percentage (e.g. 73.0% -> 73.0)
2. pct (e.g. 63.4% -> 63.4)
3. % (e.g. 89.3% -> 89.3)
4. CGPA (e.g. 7.7 / 10 -> 77.0)
5. Raw Marks (e.g. 21.6 / 50 -> 43.2)
6. Letter Grade (analytical midpoint proxy: A+=95, A=85, B=75, C=65, D=50, E=35)

Enables sensitivity analysis separating deterministic numeric scores from proxy-mapped letter grades.
"""

import re
from typing import Any, Optional, Tuple
import pandas as pd
from src.config import LETTER_GRADE_PROXY, SUBJECT_MAPPING
from src.cleaning.ids import normalize_school_id
from src.cleaning.dates import parse_date

def standardize_subject(val: Any) -> Tuple[str, str]:
    """Map raw subject string to canonical subject name."""
    if pd.isna(val):
        return "Unknown", "SUBJECT_IS_NULL"
    s = str(val).strip().lower()
    if s in SUBJECT_MAPPING:
        return SUBJECT_MAPPING[s], "MAPPED_CANONICAL_SUBJECT"
    return str(val).strip().title(), "UNMAPPED_SUBJECT_TITLECASED"

def normalize_academic_score(
    score_val: Any,
    scale_val: Any,
    max_marks_val: Any = None,
) -> Tuple[Optional[float], str, str, bool]:
    """Normalize a raw score from any grading scale to percentage (0.0 - 100.0).

    Returns:
        Tuple of (normalized_score_pct, normalization_method, quality_flag, is_letter_grade_proxy)
    """
    if pd.isna(score_val):
        return None, "MISSING", "SCORE_IS_NULL", False

    scale_str = str(scale_val).strip() if pd.notna(scale_val) else "UNKNOWN"
    score_str = str(score_val).strip()

    # 1. Percentage scales (Percentage, pct, %)
    if scale_str in ("Percentage", "pct", "%") or "%" in score_str:
        clean_num = score_str.replace("%", "").strip()
        try:
            score = float(clean_num)
            if 0.0 <= score <= 100.0:
                return score, "PERCENTAGE_DIRECT", "SCORE_PARSED_PERCENTAGE", False
            return None, "PERCENTAGE_DIRECT", f"OUT_OF_RANGE: {score}", False
        except ValueError:
            return None, "PERCENTAGE_DIRECT", f"UNPARSEABLE_PERCENTAGE: {score_str}", False

    # 2. CGPA (10 point scale)
    if scale_str == "CGPA":
        try:
            cgpa = float(score_str)
            # Standard conversion: (CGPA / 10.0) * 100.0 = CGPA * 10.0
            score = round(cgpa * 10.0, 2)
            if 0.0 <= score <= 100.0:
                return score, "CGPA_TO_PERCENT", "SCORE_SCALED_CGPA_10", False
            return None, "CGPA_TO_PERCENT", f"OUT_OF_RANGE_CGPA: {cgpa}", False
        except ValueError:
            return None, "CGPA_TO_PERCENT", f"UNPARSEABLE_CGPA: {score_str}", False

    # 3. Raw Marks (numerator / denominator)
    if scale_str == "Raw Marks" or "/" in score_str:
        m = re.match(r"([\d\.]+)\s*/\s*([\d\.]+)", score_str)
        if m:
            num = float(m.group(1))
            den = float(m.group(2))
            if den > 0:
                score = round((num / den) * 100.0, 2)
                if 0.0 <= score <= 100.0:
                    return score, "RAW_MARKS_TO_PERCENT", "SCORE_PARSED_FRACTION", False
                return None, "RAW_MARKS_TO_PERCENT", f"OUT_OF_RANGE_RATIO: {score}", False
            return None, "RAW_MARKS_TO_PERCENT", "ZERO_DENOMINATOR", False
        # Fallback to max_marks column
        try:
            num = float(score_str)
            den = float(max_marks_val) if pd.notna(max_marks_val) and float(max_marks_val) > 0 else 100.0
            score = round((num / den) * 100.0, 2)
            if 0.0 <= score <= 100.0:
                return score, "RAW_MARKS_TO_PERCENT", "SCORE_DIVIDED_BY_MAX_MARKS", False
            return None, "RAW_MARKS_TO_PERCENT", f"OUT_OF_RANGE: {score}", False
        except (ValueError, TypeError):
            return None, "RAW_MARKS_TO_PERCENT", f"UNPARSEABLE_RAW_MARKS: {score_str}", False

    # 4. Letter Grade (Analytical Mid-Point Proxy)
    if scale_str == "Letter Grade" or score_str.upper() in LETTER_GRADE_PROXY:
        grade_clean = score_str.upper()
        if grade_clean in LETTER_GRADE_PROXY:
            proxy_score = LETTER_GRADE_PROXY[grade_clean]
            return (
                proxy_score,
                "LETTER_GRADE_PROXY",
                f"MIDPOINT_PROXY_MAPPING: {grade_clean}={proxy_score}",
                True,
            )
        return None, "LETTER_GRADE_PROXY", f"UNRECOGNIZED_LETTER_GRADE: {grade_clean}", True

    return None, "UNKNOWN_SCALE", f"UNSUPPORTED_SCALE: {scale_str}", False

def clean_assessment_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, list[dict]]:
    """Clean assessment dataframe, normalize scores, map subjects, and produce audit records.

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

    # 2. Date parsing
    parsed_dates = [parse_date(d) for d in df["date"]]
    df["date_raw"] = df["date"]
    df["date"] = [p[0].isoformat() if p[0] else None for p in parsed_dates]

    # 3. Subject standardization
    subjects = [standardize_subject(s) for s in df["subject"]]
    df["subject_raw"] = df["subject"]
    df["subject_standard"] = [s[0] for s in subjects]

    # 4. Grade clean
    df["grade_raw"] = df["grade"]
    df["grade"] = pd.to_numeric(df["grade"], errors="coerce").fillna(0).astype(int)

    # 5. Score normalization
    df["avg_score_raw"] = [str(s) if pd.notna(s) else None for s in df["avg_score"]]
    df["grading_scale_raw"] = [str(g) if pd.notna(g) else None for g in df["grading_scale"]]
    df["max_marks_raw"] = [str(m) if pd.notna(m) else None for m in df["max_marks"]]
    df["max_marks"] = pd.to_numeric(df["max_marks"], errors="coerce")

    norm_scores = []
    norm_methods = []
    quality_flags = []
    is_letter_grades = []

    for idx, row in df.iterrows():
        score_val, method, flag, is_lg = normalize_academic_score(
            row["avg_score"],
            row["grading_scale"],
            row.get("max_marks"),
        )
        norm_scores.append(score_val)
        norm_methods.append(method)
        quality_flags.append(flag)
        is_letter_grades.append(is_lg)

        if is_lg:
            audit_entries.append({
                "dataset": "track4_test_scores.json",
                "record_id": str(row.get("assessment_id", f"TST_{idx}")),
                "field_name": "avg_score",
                "raw_value": str(row["avg_score"]),
                "clean_value": score_val,
                "transformation": "MAP_LETTER_GRADE_PROXY",
                "rule": f"{row['avg_score']} -> {score_val}% analytical midpoint",
                "status": "RESCUED",
                "quality_flag": "SCORE_LETTER_GRADE_PROXY",
                "reason": "Letter grade mapped to analytical mid-point proxy for cross-sectional comparison.",
            })

    df["normalized_score_pct"] = norm_scores
    df["score_normalization_method"] = norm_methods
    df["score_quality_flag"] = quality_flags
    df["is_letter_grade_proxy"] = is_letter_grades

    # 6. Quality status
    df["quality_status"] = [
        "VALID" if pd.notna(s) else "INVALID_SCORE"
        for s in df["normalized_score_pct"]
    ]

    final_cols = [
        "assessment_id",
        "date",
        "date_raw",
        "school_id",
        "school_id_raw",
        "grade",
        "grade_raw",
        "subject_standard",
        "subject_raw",
        "grading_scale_raw",
        "avg_score_raw",
        "max_marks",
        "normalized_score_pct",
        "score_normalization_method",
        "is_letter_grade_proxy",
        "total_students_assessed",
        "quality_status",
    ]

    return df[final_cols], audit_entries
