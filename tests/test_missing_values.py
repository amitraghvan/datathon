"""Unit tests for missing value resolution and district imputation."""

import pandas as pd
from src.cleaning.missing_values import clean_school_master_data, clean_infrastructure_data

def test_district_imputation_from_block():
    raw_df = pd.DataFrame([
        {
            "school_id": "SCH0205",
            "school_name": "Govt High School",
            "district": None, # Missing!
            "block": "Ferozepur",
            "total_enrolled_students": 250,
            "school_type": "secondary",
            "medium": "punjabi",
        },
        {
            "school_id": "SCH0085",
            "school_name": "Govt Primary School",
            "district": None, # Both missing!
            "block": None,
            "total_enrolled_students": 120,
            "school_type": "primary",
            "medium": "hindi",
        },
    ])

    df_clean, audit = clean_school_master_data(raw_df)

    # First row should be imputed from block 'Ferozepur' -> 'Ferozepur'
    assert df_clean.iloc[0]["district"] == "Ferozepur"
    assert df_clean.iloc[0]["district_imputation_status"] == "IMPUTED_FROM_BLOCK"
    assert df_clean.iloc[0]["school_type"] == "Secondary"
    assert df_clean.iloc[0]["medium"] == "Punjabi"

    # Second row should be 'Unknown'
    assert df_clean.iloc[1]["district"] == "Unknown"
    assert df_clean.iloc[1]["district_imputation_status"] == "UNRESOLVED"
    assert df_clean.iloc[1]["school_type"] == "Primary"
    assert df_clean.iloc[1]["medium"] == "Hindi"

    # Verify audit entries
    assert any(a["transformation"] == "IMPUTE_DISTRICT_FROM_BLOCK" for a in audit)
    assert any(a["transformation"] == "ASSIGN_UNKNOWN_DISTRICT" for a in audit)

def test_clean_infrastructure_booleans():
    raw_df = pd.DataFrame([{
        "inspection_id": "INSP001",
        "date": "2025-05-10",
        "school_id": "SCH0050",
        "has_electricity": "Haan",
        "has_drinking_water": "1",
        "has_functional_toilet": "Nahi",
        "has_boundary_wall": "Broken",
        "has_playground": None, # UNKNOWN
        "inspector_name": None,
        "remarks": None,
    }])

    df_clean, audit = clean_infrastructure_data(raw_df)
    row = df_clean.iloc[0]
    assert row["has_electricity"] == "TRUE"
    assert row["has_drinking_water"] == "TRUE"
    assert row["has_functional_toilet"] == "FALSE"
    assert row["has_boundary_wall"] == "FALSE"
    assert row["has_playground"] == "UNKNOWN"
    assert row["inspector_name"] == "Unknown Inspector"
    assert row["remarks"] == "No remarks"
