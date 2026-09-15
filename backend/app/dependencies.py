"""FastAPI request dependencies and query filter extractors."""

from typing import Any, Dict, Optional

from fastapi import Query

from backend.app.repository.duckdb import DuckDBRepository, db_repo


def get_repository() -> DuckDBRepository:
    """Dependency provider for DuckDB repository."""
    return db_repo


def get_filter_params(
    district: Optional[str] = Query(None, description="Filter by District"),
    block: Optional[str] = Query(None, description="Filter by Block"),
    school_id: Optional[str] = Query(None, description="Filter by School ID"),
    school_type: Optional[str] = Query(None, description="Filter by School Type"),
    medium: Optional[str] = Query(None, description="Filter by Medium of Instruction"),
    risk_tier: Optional[str] = Query(None, description="Filter by Risk Severity Tier"),
    primary_driver: Optional[str] = Query(None, description="Filter by Primary Risk Driver"),
    welfare_quadrant: Optional[str] = Query(None, description="Filter by Welfare Gap Matrix Quadrant"),
) -> Dict[str, Any]:
    """Extract and validate query parameters into filter dictionary."""
    filters: Dict[str, Any] = {}
    if district and district != "ALL":
        filters["district"] = district
    if block and block != "ALL":
        filters["block"] = block
    if school_id:
        filters["school_id"] = school_id
    if school_type and school_type != "ALL":
        filters["school_type"] = school_type
    if medium and medium != "ALL":
        filters["medium"] = medium
    if risk_tier and risk_tier != "ALL":
        filters["risk_tier"] = risk_tier
    if primary_driver and primary_driver != "ALL":
        filters["primary_driver"] = primary_driver
    if welfare_quadrant and welfare_quadrant != "ALL":
        filters["welfare_quadrant"] = welfare_quadrant
    return filters
