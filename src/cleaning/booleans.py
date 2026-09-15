"""Multilingual boolean normalization module.

Standardizes diverse multilingual, operational, and colloquial boolean strings
(e.g., 'Haan', 'Hai', 'Yes', '1', 'Functional', 'Nahi', 'Kharab', '0')
into canonical values: 'TRUE', 'FALSE', or 'UNKNOWN'.

Guarantees: UNKNOWN != FALSE. Missing or ambiguous values are NEVER converted to FALSE.
"""

from typing import Any, Tuple

import pandas as pd

from src.config import BOOLEAN_FALSE_TOKENS, BOOLEAN_TRUE_TOKENS


def normalize_boolean(val: Any) -> Tuple[str, str, str]:
    """Normalize a raw value to canonical 'TRUE', 'FALSE', or 'UNKNOWN'.

    Args:
        val: Input raw value.

    Returns:
        Tuple of (canonical_value, transformation_status, quality_flag)
        canonical_value in: 'TRUE', 'FALSE', 'UNKNOWN'
    """
    if pd.isna(val):
        return "UNKNOWN", "PRESERVED_UNKNOWN", "VALUE_IS_NULL"

    s = str(val).strip().lower()
    if not s or s in ("none", "nan", "null", ""):
        return "UNKNOWN", "PRESERVED_UNKNOWN", "VALUE_IS_EMPTY"

    if s in BOOLEAN_TRUE_TOKENS:
        return "TRUE", "NORMALIZED_TRUE", f"MATCHED_TRUE_TOKEN: {s}"

    if s in BOOLEAN_FALSE_TOKENS:
        return "FALSE", "NORMALIZED_FALSE", f"MATCHED_FALSE_TOKEN: {s}"

    return "UNKNOWN", "UNRECOGNIZED_TOKEN", f"UNRECOGNIZED_BOOLEAN_STRING: {s}"


def clean_boolean_series(series: pd.Series, field_prefix: str = "bool") -> pd.DataFrame:
    """Normalize a pandas Series of boolean-like strings with lineage tracking.

    Returns:
        DataFrame with columns:
        - {field_prefix}_raw
        - {field_prefix}_clean
        - {field_prefix}_status
        - {field_prefix}_flag
    """
    records = []
    for val in series:
        canon, status, flag = normalize_boolean(val)
        records.append(
            {
                f"{field_prefix}_raw": val,
                f"{field_prefix}_clean": canon,
                f"{field_prefix}_status": status,
                f"{field_prefix}_flag": flag,
            }
        )
    return pd.DataFrame(records)
