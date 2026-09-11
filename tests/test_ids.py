"""Unit tests for school ID normalization."""

import pytest
from src.cleaning.ids import normalize_school_id, clean_school_ids
import pandas as pd

@pytest.mark.parametrize(
    "raw_input, expected_id, expected_status",
    [
        ("SCH0050", "SCH0050", "ALREADY_CANONICAL"),
        ("sch_0050", "SCH0050", "NORMALIZED"),
        ("SCH-0050", "SCH0050", "NORMALIZED"),
        ("0050", "SCH0050", "NORMALIZED"),
        ("S0050", "SCH0050", "NORMALIZED"),
        ("SCH-0596", "SCH0596", "NORMALIZED"),
        ("sch_0054", "SCH0054", "NORMALIZED"),
        ("0286", "SCH0286", "NORMALIZED"),
        ("S0212", "SCH0212", "NORMALIZED"),
        ("sch0505", "SCH0505", "NORMALIZED"),
        ("  SCH-0433  ", "SCH0433", "NORMALIZED"),
        ("SCH1", "SCH0001", "NORMALIZED"),
        (None, None, "MISSING"),
        ("", None, "MISSING"),
        ("INVALID_TEXT", None, "INVALID"),
    ],
)
def test_normalize_school_id(raw_input, expected_id, expected_status):
    canon_id, status, reason = normalize_school_id(raw_input)
    assert canon_id == expected_id
    assert status == expected_status
    assert isinstance(reason, str)

def test_clean_school_ids_dataframe():
    series = pd.Series(["SCH0050", "sch_0054", "SCH-0596", None])
    df_clean = clean_school_ids(series)
    assert list(df_clean.columns) == [
        "school_id_raw",
        "school_id",
        "id_normalization_status",
        "id_quality_flag",
    ]
    assert df_clean["school_id"].iloc[0] == "SCH0050"
    assert df_clean["school_id"].iloc[1] == "SCH0054"
    assert df_clean["school_id"].iloc[2] == "SCH0596"
    assert pd.isna(df_clean["school_id"].iloc[3])
    assert df_clean["id_normalization_status"].tolist() == [
        "ALREADY_CANONICAL",
        "NORMALIZED",
        "NORMALIZED",
        "MISSING",
    ]
