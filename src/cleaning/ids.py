"""School ID normalization and entity resolution.

Standardizes diverse school ID representations (e.g. SCH-0596, sch_0054, 0286, S0212)
into canonical format 'SCH' followed by a 4-digit zero-padded identifier ('SCH0596').
Preserves full lineage and auditability.
"""

import re
from typing import Any, Tuple

import pandas as pd

CANONICAL_ID_REGEX = re.compile(r"^SCH\d{4}$")


def normalize_school_id(val: Any) -> Tuple[str | None, str, str]:
    """Normalize a single school ID value.

    Args:
        val: Raw school ID input.

    Returns:
        Tuple of (canonical_id, status, reason)
        status in: ALREADY_CANONICAL, NORMALIZED, MISSING, INVALID
    """
    if pd.isna(val):
        return None, "MISSING", "VALUE_IS_NULL"

    s = str(val).strip()
    if not s:
        return None, "MISSING", "VALUE_IS_EMPTY_STRING"

    # Check if already canonical
    if CANONICAL_ID_REGEX.match(s):
        return s, "ALREADY_CANONICAL", "MATCHES_CANONICAL_PATTERN"

    # Extract digits
    digits = re.findall(r"\d+", s)
    if not digits:
        return None, "INVALID", f"NO_NUMERIC_IDENTIFIER_FOUND: {s}"

    # Take the last contiguous digit sequence (e.g., in SCH-0050 -> 0050)
    num_str = digits[-1]
    num = int(num_str)
    canonical = f"SCH{num:04d}"

    # Determine specific transformation reason
    s_upper = s.upper()
    if s_upper.startswith("SCH-"):
        reason = "STRIPPED_HYPHEN_PREFIX"
    elif s_upper.startswith("SCH_") or s.lower().startswith("sch_"):
        reason = "STRIPPED_UNDERSCORE_PREFIX"
    elif s_upper.startswith("S") and not s_upper.startswith("SCH"):
        reason = "REPLACED_SINGLE_S_PREFIX"
    elif s.isdigit():
        reason = "ZERO_PADDED_NUMERIC_ID"
    elif s.islower() and s_upper.startswith("SCH"):
        reason = "UPPERCASED_PREFIX"
    else:
        reason = "STANDARDIZED_ALPHANUMERIC_STRING"

    return canonical, "NORMALIZED", reason


def clean_school_ids(series: pd.Series) -> pd.DataFrame:
    """Vectorized / batch normalization of a school ID Series with lineage.

    Returns:
        DataFrame with columns:
        - school_id_raw
        - school_id
        - id_normalization_status
        - id_quality_flag
    """
    results = [normalize_school_id(v) for v in series]
    df_res = pd.DataFrame(
        results, columns=["school_id", "id_normalization_status", "id_quality_flag"]
    )
    df_res["school_id_raw"] = series.values
    return df_res[["school_id_raw", "school_id", "id_normalization_status", "id_quality_flag"]]
