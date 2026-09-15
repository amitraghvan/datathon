"""Unit tests for date parsing and calendar enrichment."""

import pytest

from src.cleaning.dates import clean_dates_dataframe, parse_date


@pytest.mark.parametrize(
    "raw_date, expected_iso, expected_fmt",
    [
        ("2025-04-21", "2025-04-21", "YYYY-MM-DD"),
        ("2025/05/19", "2025-05-19", "YYYY/MM/DD"),
        ("17.05.2025", "2025-05-17", "DD.MM.YYYY"),
        ("30/07/2025", "2025-07-30", "DD/MM/YYYY"),
        ("07-26-2025", "2025-07-26", "MM-DD-YYYY"),
        ("11-Sep-2025", "2025-09-11", "DD-Mon-YYYY"),
        ("  2026-03-31  ", "2026-03-31", "YYYY-MM-DD"),
    ],
)
def test_parse_date_valid(raw_date, expected_iso, expected_fmt):
    dt, status, fmt_name, flag = parse_date(raw_date)
    assert dt is not None
    assert dt.isoformat() == expected_iso
    assert status == "SUCCESS"
    assert fmt_name == expected_fmt


def test_parse_date_invalid_and_missing():
    dt, status, fmt_name, flag = parse_date(None)
    assert dt is None
    assert status == "MISSING"

    dt, status, fmt_name, flag = parse_date("not-a-date")
    assert dt is None
    assert status == "FAILED"


def test_clean_dates_dataframe_calendar_attributes():
    import pandas as pd

    series = pd.Series(
        ["2025-05-04", "2025-08-30"]
    )  # 2025-05-04 is a Sunday, 2025-08-30 is a Saturday
    df_clean = clean_dates_dataframe(series)
    assert df_clean["date"].tolist() == ["2025-05-04", "2025-08-30"]
    assert df_clean["day_of_week"].tolist() == ["Sunday", "Saturday"]
    assert df_clean["is_sunday"].tolist() == [True, False]
    assert df_clean["is_weekend"].tolist() == [True, True]
    assert df_clean["month_name"].tolist() == ["May", "August"]
