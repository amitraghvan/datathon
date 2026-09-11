"""Unit tests for MDM unit conversion, currency cleaning, and value rescue."""

import pandas as pd
import pytest
from src.cleaning.units import (
    clean_currency,
    parse_quantity_and_unit,
    standardize_grain_name,
    standardize_vendor,
    clean_procurement_data,
)

def test_clean_currency():
    assert clean_currency("Rs. 1,600")[0] == 1600.0
    assert clean_currency("₹644")[0] == 644.0
    assert clean_currency("336/-")[0] == 336.0
    assert clean_currency("1,710/-")[0] == 1710.0
    assert clean_currency("596")[0] == 596.0
    assert clean_currency(None)[0] is None

def test_parse_quantity_and_unit():
    # Embedded strings
    q1, u1, _, r1 = parse_quantity_and_unit("14.9 kg", None)
    assert q1 == 14.9
    assert u1 == "kg"

    q2, u2, _, _ = parse_quantity_and_unit("500 g", None)
    assert q2 == 0.5

    q3, u3, _, _ = parse_quantity_and_unit(2, "50kg Bags")
    assert q3 == 100.0

    q4, u4, _, _ = parse_quantity_and_unit(3, "Sacks")
    assert q4 == 150.0

    q5, u5, _, _ = parse_quantity_and_unit(1, "Bori")
    assert q5 == 50.0

def test_standardize_grain_name():
    assert standardize_grain_name("Chawal")[0] == "Rice"
    assert standardize_grain_name("RICE")[0] == "Rice"
    assert standardize_grain_name("Atta")[0] == "Wheat"
    assert standardize_grain_name("Gehun")[0] == "Wheat"
    assert standardize_grain_name("Dal")[0] == "Pulses"
    assert standardize_grain_name("Sarson Tel")[0] == "Cooking Oil"
    assert standardize_grain_name("Mustard Oil")[0] == "Cooking Oil"

def test_standardize_vendor():
    v1, id1, _ = standardize_vendor("sharma traders pvt ltd")
    assert v1 == "Sharma Traders"
    assert id1 == "VEN003"

    v2, id2, _ = standardize_vendor("kumar general store")
    assert v2 == "Kumar Supplies"
    assert id2 == "VEN001"

def test_procurement_value_rescue():
    # Test missing quantity derivation via cost / price
    # Cooking Oil price is ₹120/kg. Cost = 1200 => quantity should be 10 kg
    raw_df = pd.DataFrame([{
        "procurement_id": "MDM99901",
        "date": "2025-08-10",
        "school_id": "SCH0050",
        "vendor_name": "Sharma Traders",
        "grain_type": "Cooking Oil",
        "quantity": None,
        "unit": None,
        "total_cost": "Rs. 1,200",
        "payment_status": "Paid",
    }])

    df_clean, audit = clean_procurement_data(raw_df)
    row = df_clean.iloc[0]
    assert row["quantity_kg"] == 10.0
    assert row["quantity_rescue_method"] == "DERIVED_FROM_COST"
    assert any(a["transformation"] == "DERIVE_QUANTITY_FROM_COST" for a in audit)

    # Test missing cost derivation via quantity * price
    # Wheat price is ₹30/kg. Quantity = 50 kg => cost should be ₹1500
    raw_df2 = pd.DataFrame([{
        "procurement_id": "MDM99902",
        "date": "2025-08-10",
        "school_id": "SCH0050",
        "vendor_name": "Kumar Supplies",
        "grain_type": "Wheat",
        "quantity": 50.0,
        "unit": "kg",
        "total_cost": None,
        "payment_status": "Pending",
    }])

    df_clean2, audit2 = clean_procurement_data(raw_df2)
    row2 = df_clean2.iloc[0]
    assert row2["total_cost"] == 1500.0
    assert row2["cost_rescue_method"] == "DERIVED_FROM_QUANTITY"
    assert any(a["transformation"] == "DERIVE_COST_FROM_QUANTITY" for a in audit2)
