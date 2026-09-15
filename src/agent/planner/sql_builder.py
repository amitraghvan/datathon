"""Controlled, safe SQL query builder restricted strictly to approved analytical views."""

from typing import Any, Dict, List, Optional, Tuple

from backend.app.repository.queries import (
    DISTRICT_SUMMARY_SQL,
    PROCUREMENT_ENRICHED_SQL,
    SCHOOL_MASTER_ENRICHED_SQL,
)

APPROVED_VIEWS = {
    "school_master_enriched": SCHOOL_MASTER_ENRICHED_SQL,
    "district_performance": DISTRICT_SUMMARY_SQL,
    "procurement_summary": PROCUREMENT_ENRICHED_SQL,
}


def build_filtered_query(
    base_sql: str,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: int = 10,
) -> Tuple[str, List[Any]]:
    """Wrap governed base view in a controlled outer filter and order specification."""
    clauses: List[str] = []
    params: List[Any] = []

    if filters:
        for key, val in filters.items():
            if val is None or val == "" or val == "ALL":
                continue

            if key == "district":
                if isinstance(val, list):
                    placeholders = ", ".join(["?"] * len(val))
                    clauses.append(f"district IN ({placeholders})")
                    params.extend(val)
                else:
                    clauses.append("district = ?")
                    params.append(val)
            elif key == "school_id":
                if isinstance(val, list):
                    placeholders = ", ".join(["?"] * len(val))
                    clauses.append(f"school_id IN ({placeholders})")
                    params.extend(val)
                else:
                    clauses.append("school_id = ?")
                    params.append(val)
            elif key == "block":
                clauses.append("block = ?")
                params.append(val)
            elif key == "school_type":
                clauses.append("school_type = ?")
                params.append(val)
            elif key == "medium":
                clauses.append("medium = ?")
                params.append(val)
            elif key == "risk_tier":
                clauses.append("risk_tier = ?")
                params.append(val)
            elif key == "primary_driver":
                clauses.append("primary_driver = ?")
                params.append(val)
            elif key == "welfare_quadrant":
                clauses.append("welfare_quadrant = ?")
                params.append(val)
            elif key == "amenity":
                if val in ["electricity", "drinking_water", "functional_toilet", "boundary_wall", "playground"]:
                    clauses.append(f"{val} = TRUE")
            elif key == "missing_amenity":
                if val in ["electricity", "drinking_water", "functional_toilet", "boundary_wall", "playground"]:
                    clauses.append(f"{val} = FALSE")
            elif key in ["electricity", "drinking_water", "functional_toilet", "boundary_wall", "playground"]:
                if val is False or str(val).lower() in ["false", "missing", "0", "none"]:
                    clauses.append(f"{key} = FALSE")
                elif val is True or str(val).lower() in ["true", "available", "1"]:
                    clauses.append(f"{key} = TRUE")

    where_str = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order_str = f"ORDER BY {order_by}" if order_by else ""
    safe_limit = max(1, min(limit, 100))

    query = f"""
    WITH base_dataset AS (
        {base_sql}
    )
    SELECT *
    FROM base_dataset
    {where_str}
    {order_str}
    LIMIT {safe_limit};
    """
    return query, params
