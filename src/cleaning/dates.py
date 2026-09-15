"""Date normalization and calendar dimension enrichment.

De-obfuscates the six observed date formats in the competition datasets:
1. YYYY-MM-DD (e.g. 2025-04-21)
2. YYYY/MM/DD (e.g. 2025/05/19)
3. DD.MM.YYYY (e.g. 17.05.2025)
4. DD/MM/YYYY (e.g. 30/07/2025)
5. MM-DD-YYYY (e.g. 07-26-2025)
6. DD-Mon-YYYY (e.g. 11-Sep-2025)

Enriches canonical dates with calendar attributes and maintains lineage metadata.
"""

import re
from datetime import date, datetime
from typing import Any, Optional, Tuple

import pandas as pd

DATE_PATTERNS = [
    ("YYYY-MM-DD", re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d"),
    ("YYYY/MM/DD", re.compile(r"^\d{4}/\d{2}/\d{2}$"), "%Y/%m/%d"),
    ("DD.MM.YYYY", re.compile(r"^\d{2}\.\d{2}\.\d{4}$"), "%d.%m.%Y"),
    ("DD/MM/YYYY", re.compile(r"^\d{2}/\d{2}/\d{4}$"), "%d/%m/%Y"),
    ("MM-DD-YYYY", re.compile(r"^\d{2}-\d{2}-\d{4}$"), "%m-%d-%Y"),
    ("DD-Mon-YYYY", re.compile(r"^\d{2}-[A-Za-z]{3}-\d{4}$"), "%d-%b-%Y"),
]


def parse_date(val: Any) -> Tuple[Optional[date], str, str, str]:
    """Parse raw date string into canonical datetime.date.

    Returns:
        Tuple of (date_obj, date_parse_status, date_format_detected, date_quality_flag)
    """
    if pd.isna(val):
        return None, "MISSING", "NONE", "VALUE_IS_NULL"

    s = str(val).strip()
    if not s:
        return None, "MISSING", "NONE", "VALUE_IS_EMPTY"

    for fmt_name, regex, strptime_fmt in DATE_PATTERNS:
        if regex.match(s):
            try:
                dt = datetime.strptime(s, strptime_fmt).date()
                return dt, "SUCCESS", fmt_name, f"PARSED_{fmt_name}"
            except ValueError as e:
                return None, "FAILED", fmt_name, f"VALUE_ERROR: {e}"

    return None, "FAILED", "UNRECOGNIZED", f"NO_MATCHING_PATTERN: {s}"


def clean_dates_dataframe(series: pd.Series) -> pd.DataFrame:
    """Vectorized date normalization returning canonical date and calendar attributes.

    Returns:
        DataFrame with columns:
        - date_raw
        - date (YYYY-MM-DD string)
        - year
        - month
        - month_name
        - quarter
        - week
        - day_of_week
        - is_weekend
        - is_sunday
        - date_parse_status
        - date_format_detected
        - date_quality_flag
    """
    records = []
    for val in series:
        dt, status, fmt_name, flag = parse_date(val)
        if dt is not None:
            rec = {
                "date_raw": val,
                "date": dt.isoformat(),
                "year": dt.year,
                "month": dt.month,
                "month_name": dt.strftime("%B"),
                "quarter": (dt.month - 1) // 3 + 1,
                "week": dt.isocalendar()[1],
                "day_of_week": dt.strftime("%A"),
                "is_weekend": dt.weekday() in (5, 6),
                "is_sunday": dt.weekday() == 6,
                "date_parse_status": status,
                "date_format_detected": fmt_name,
                "date_quality_flag": flag,
            }
        else:
            rec = {
                "date_raw": val,
                "date": None,
                "year": None,
                "month": None,
                "month_name": None,
                "quarter": None,
                "week": None,
                "day_of_week": None,
                "is_weekend": None,
                "is_sunday": None,
                "date_parse_status": status,
                "date_format_detected": fmt_name,
                "date_quality_flag": flag,
            }
        records.append(rec)

    return pd.DataFrame(records)
