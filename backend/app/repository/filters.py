"""Filter building utilities for DuckDB SQL execution."""

from typing import Any, Dict, List, Tuple


def build_where_clause(filters: Dict[str, Any], table_alias: str = "") -> Tuple[str, List[Any]]:
    """Build a parameterized SQL WHERE clause based on provided filter parameters."""
    conditions: List[str] = []
    params: List[Any] = []
    prefix = f"{table_alias}." if table_alias else ""

    if filters.get("district") and filters["district"] != "ALL":
        conditions.append(f"{prefix}district = ?")
        params.append(filters["district"])

    if filters.get("block") and filters["block"] != "ALL":
        conditions.append(f"{prefix}block = ?")
        params.append(filters["block"])

    if filters.get("school_type") and filters["school_type"] != "ALL":
        conditions.append(f"{prefix}school_type = ?")
        params.append(filters["school_type"])

    if filters.get("medium") and filters["medium"] != "ALL":
        conditions.append(f"{prefix}medium = ?")
        params.append(filters["medium"])

    if filters.get("risk_tier") and filters["risk_tier"] != "ALL":
        conditions.append(f"{prefix}risk_tier = ?")
        params.append(filters["risk_tier"])

    if filters.get("primary_driver") and filters["primary_driver"] != "ALL":
        conditions.append(f"{prefix}primary_driver = ?")
        params.append(filters["primary_driver"])

    if filters.get("welfare_quadrant") and filters["welfare_quadrant"] != "ALL":
        conditions.append(f"{prefix}welfare_quadrant = ?")
        params.append(filters["welfare_quadrant"])

    if not conditions:
        return "1=1", []

    return " AND ".join(conditions), params
