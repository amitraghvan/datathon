"""MDM procurement cleaning, unit conversion, currency standardization, and value rescue engine.

Handles:
1. Currency normalization (strips 'Rs.', '₹', '/-', commas, whitespace).
2. Embedded unit extraction from text (e.g. '14.9 kg' -> 14.9 kg).
3. Unit conversions to standard Kilograms:
   - Grams / g -> / 1000.0
   - 50kg Bags / Sacks / Bori -> * 50.0
   - kg / kgs / KG -> 1.0
4. Grain classification into canonical commodities (Wheat, Rice, Pulses, Cooking Oil).
5. Missing quantity derivation: quantity_kg = total_cost / price_per_kg.
6. Missing cost derivation: total_cost = quantity_kg * price_per_kg.
7. Vendor entity resolution (12 strings -> 4 entities).
8. Preserves full lineage and audit trails.
"""

import re
from typing import Any, Optional, Tuple
import pandas as pd
from src.config import (
    GRAIN_TYPE_MAPPING,
    GRAIN_UNIT_PRICES,
    VENDOR_MAPPING,
)
from src.cleaning.ids import normalize_school_id
from src.cleaning.dates import parse_date

VENDOR_ID_MAP = {
    "Kumar Supplies": "VEN001",
    "Singh Agro": "VEN002",
    "Sharma Traders": "VEN003",
    "Goyal Rice Mill": "VEN004",
}

def clean_currency(val: Any) -> Tuple[Optional[float], str, str]:
    """Parse messy currency strings to numeric float INR.

    Examples:
        'Rs. 1,600' -> 1600.0
        '₹644' -> 644.0
        '336/-' -> 336.0
    """
    if pd.isna(val):
        return None, "MISSING", "VALUE_IS_NULL"

    if isinstance(val, (int, float)):
        return float(val), "NUMERIC_DIRECT", "NATIVE_NUMERIC"

    s = str(val).strip()
    if not s:
        return None, "MISSING", "VALUE_IS_EMPTY"

    # Remove currency markers and formatting
    cleaned = (
        s.replace("Rs.", "")
        .replace("Rs", "")
        .replace("₹", "")
        .replace("/-", "")
        .replace(",", "")
        .strip()
    )

    try:
        cost_float = float(cleaned)
        return cost_float, "NORMALIZED", "PARSED_CURRENCY_STRING"
    except ValueError:
        return None, "INVALID", f"COULD_NOT_PARSE_CURRENCY: {s}"

def standardize_grain_name(val: Any) -> Tuple[str, str]:
    """Map raw grain string to canonical commodity."""
    if pd.isna(val):
        return "Unknown", "GRAIN_IS_NULL"
    s = str(val).strip().lower()
    if s in GRAIN_TYPE_MAPPING:
        return GRAIN_TYPE_MAPPING[s], "MAPPED_CANONICAL_GRAIN"
    return str(val).strip().title(), "UNMAPPED_GRAIN_TITLECASED"

def standardize_vendor(val: Any) -> Tuple[str, str, str]:
    """Map raw vendor name to canonical vendor entity and vendor_id."""
    if pd.isna(val):
        return "Unknown Vendor", "VEN000", "VENDOR_IS_NULL"
    s = str(val).strip().lower()
    canon_name = VENDOR_MAPPING.get(s, str(val).strip().title())
    vendor_id = VENDOR_ID_MAP.get(canon_name, "VEN999")
    return canon_name, vendor_id, "RESOLVED_VENDOR_ENTITY"

def parse_quantity_and_unit(qty_raw: Any, unit_raw: Any) -> Tuple[Optional[float], str, str, str]:
    """Extract numeric quantity in kg and standard unit.

    Handles embedded strings (e.g. '14.9 kg') and converts sacks/grams to kg.
    """
    qty_num: Optional[float] = None
    detected_unit = "kg"
    conversion_reason = "EXACT_KG"

    # 1. Check if quantity is a string with embedded units
    if isinstance(qty_raw, str):
        s = qty_raw.strip()
        m_kg = re.search(r"([\d\.]+)\s*(?:kg|kgs|kilogram)", s, re.IGNORECASE)
        m_g = re.search(r"([\d\.]+)\s*(?:g|gram|grams)", s, re.IGNORECASE)
        m_bag = re.search(r"([\d\.]+)\s*(?:bag|bags|sack|sacks|bori)", s, re.IGNORECASE)

        if m_kg:
            qty_num = float(m_kg.group(1))
            detected_unit = "kg"
            conversion_reason = "EXTRACTED_EMBEDDED_KG"
        elif m_g:
            qty_num = float(m_g.group(1)) / 1000.0
            detected_unit = "kg"
            conversion_reason = "CONVERTED_EMBEDDED_GRAMS_TO_KG"
        elif m_bag:
            qty_num = float(m_bag.group(1)) * 50.0
            detected_unit = "kg"
            conversion_reason = "CONVERTED_EMBEDDED_BAGS_TO_KG"
        else:
            try:
                qty_num = float(s)
            except ValueError:
                qty_num = None

    elif isinstance(qty_raw, (int, float)) and not pd.isna(qty_raw):
        qty_num = float(qty_raw)

    # 2. If quantity parsed, apply external unit if provided
    if qty_num is not None and pd.notna(unit_raw) and conversion_reason == "EXACT_KG":
        u_str = str(unit_raw).strip().lower()
        if any(w in u_str for w in ["bag", "sack", "bori"]):
            qty_num = qty_num * 50.0
            detected_unit = "kg"
            conversion_reason = "CONVERTED_50KG_BAGS_TO_KG"
        elif any(w in u_str for w in ["gram", "grams"]) or u_str == "g":
            qty_num = qty_num / 1000.0
            detected_unit = "kg"
            conversion_reason = "CONVERTED_GRAMS_TO_KG"
        elif any(w in u_str for w in ["kg", "kgs", "kilogram"]):
            detected_unit = "kg"
            conversion_reason = "EXACT_KG"

    if qty_num is not None:
        return qty_num, detected_unit, "CONVERTED", conversion_reason
    return None, "kg", "MISSING", "QUANTITY_IS_NULL"

def clean_procurement_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, list[dict]]:
    """Execute complete traceable procurement cleaning, value rescue, and entity mapping.

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

    # 3. Vendor entity resolution
    vendors = [standardize_vendor(v) for v in df["vendor_name"]]
    df["vendor_name_raw"] = df["vendor_name"]
    df["vendor_name"] = [v[0] for v in vendors]
    df["vendor_id"] = [v[1] for v in vendors]

    # 4. Grain type standardization & benchmark price assignment
    grains = [standardize_grain_name(g) for g in df["grain_type"]]
    df["grain_raw"] = df["grain_type"]
    df["grain_standard"] = [g[0] for g in grains]
    df["price_per_kg"] = [GRAIN_UNIT_PRICES.get(g[0], None) for g in grains]

    # 5. Currency normalization
    costs = [clean_currency(c) for c in df["total_cost"]]
    df["total_cost_raw"] = [str(c) if pd.notna(c) else None for c in df["total_cost"]]
    df["total_cost"] = [c[0] for c in costs]
    df["cost_status"] = [c[1] for c in costs]

    # 6. Quantity parsing & unit standardization
    df["quantity_raw"] = [str(q) if pd.notna(q) else None for q in df["quantity"]]
    df["unit_raw"] = [str(u) if pd.notna(u) else None for u in df["unit"]]
    qty_parsed = [parse_quantity_and_unit(q, u) for q, u in zip(df["quantity"], df["unit"])]
    df["quantity_kg"] = [q[0] for q in qty_parsed]
    df["unit_standard"] = [q[1] for q in qty_parsed]
    df["conversion_status"] = [q[2] for q in qty_parsed]
    df["conversion_reason"] = [q[3] for q in qty_parsed]

    # 7. VALUE RESCUE LOGIC:
    # A. Missing quantity derivation via total_cost / price_per_kg
    # B. Missing cost derivation via quantity_kg * price_per_kg
    quantity_rescue_methods = []
    cost_rescue_methods = []

    for idx, row in df.iterrows():
        q = row["quantity_kg"]
        c = row["total_cost"]
        price = row["price_per_kg"]
        proc_id = str(row["procurement_id"])

        q_method = "ORIGINAL_STANDARDIZED"
        c_method = "ORIGINAL_STANDARDIZED"

        # Case 1: Missing quantity but valid cost and price
        if pd.isna(q) and pd.notna(c) and price and price > 0:
            derived_q = round(c / price, 2)
            df.at[idx, "quantity_kg"] = derived_q
            q_method = "DERIVED_FROM_COST"
            audit_entries.append({
                "dataset": "track4_mid_day_meal_procurement.xlsx",
                "record_id": proc_id,
                "field_name": "quantity_kg",
                "raw_value": None,
                "clean_value": derived_q,
                "transformation": "DERIVE_QUANTITY_FROM_COST",
                "rule": f"quantity_kg = total_cost ({c}) / price_per_kg ({price})",
                "status": "RESCUED",
                "quality_flag": "QTY_DERIVED_FROM_COST",
                "reason": "Quantity was missing; mathematically derived from standard commodity unit price.",
            })

        # Case 2: Missing cost but valid quantity and price
        elif pd.isna(c) and pd.notna(q) and price and price > 0:
            derived_c = round(q * price, 2)
            df.at[idx, "total_cost"] = derived_c
            c_method = "DERIVED_FROM_QUANTITY"
            audit_entries.append({
                "dataset": "track4_mid_day_meal_procurement.xlsx",
                "record_id": proc_id,
                "field_name": "total_cost",
                "raw_value": None,
                "clean_value": derived_c,
                "transformation": "DERIVE_COST_FROM_QUANTITY",
                "rule": f"total_cost = quantity_kg ({q}) * price_per_kg ({price})",
                "status": "RESCUED",
                "quality_flag": "COST_DERIVED_FROM_QTY",
                "reason": "Total cost was missing; mathematically derived from standard commodity unit price.",
            })

        quantity_rescue_methods.append(q_method)
        cost_rescue_methods.append(c_method)

    df["quantity_rescue_method"] = quantity_rescue_methods
    df["cost_rescue_method"] = cost_rescue_methods

    # 8. Payment status normalization
    def clean_payment_status(val: Any) -> str:
        if pd.isna(val):
            return "UNKNOWN"
        s = str(val).strip().lower()
        if s in ("paid", "cleared"):
            return "CLEARED"
        if s in ("due", "pending"):
            return "PENDING"
        return "UNKNOWN"

    df["payment_status_raw"] = df["payment_status"]
    df["payment_status"] = df["payment_status"].apply(clean_payment_status)

    # 9. Quality status
    df["quality_status"] = [
        "VALID" if pd.notna(q) and pd.notna(c) else "INCOMPLETE"
        for q, c in zip(df["quantity_kg"], df["total_cost"])
    ]

    final_cols = [
        "procurement_id",
        "date",
        "date_raw",
        "school_id",
        "school_id_raw",
        "vendor_id",
        "vendor_name",
        "vendor_name_raw",
        "grain_standard",
        "grain_raw",
        "quantity_kg",
        "quantity_raw",
        "unit_standard",
        "unit_raw",
        "price_per_kg",
        "total_cost",
        "total_cost_raw",
        "payment_status",
        "payment_status_raw",
        "quantity_rescue_method",
        "cost_rescue_method",
        "quality_status",
    ]

    return df[final_cols], audit_entries
