"""Unit tests for deduplication and audit logging."""

import pandas as pd

from src.cleaning.duplicates import deduplicate_dataframe


def test_deduplicate_exact_rows():
    df = pd.DataFrame([
        {"school_id": "SCH001", "name": "School 1", "score": 80},
        {"school_id": "SCH001", "name": "School 1", "score": 80}, # Exact dup
        {"school_id": "SCH002", "name": "School 2", "score": 90},
    ])

    df_clean, audit = deduplicate_dataframe(df, "test_dataset", key_col="school_id")
    assert len(df_clean) == 2
    assert len(audit) == 1
    assert audit[0]["transformation"] == "REMOVE_EXACT_DUPLICATE"

def test_deduplicate_no_duplicates():
    df = pd.DataFrame([
        {"school_id": "SCH001", "score": 80},
        {"school_id": "SCH002", "score": 90},
    ])
    df_clean, audit = deduplicate_dataframe(df, "test_dataset", key_col="school_id")
    assert len(df_clean) == 2
    assert len(audit) == 0
