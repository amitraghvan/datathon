"""Risk Severity and Intervention Prioritization endpoints."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import get_filter_params, get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.risk import (
    DriverDistributionItem,
    PrioritySchoolItem,
    RiskSummaryResponse,
)
from backend.app.services.risk_service import RiskService

router = APIRouter()


@router.get("/summary", response_model=RiskSummaryResponse, summary="Get operational triaging and driver overview")
def get_risk_summary(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> RiskSummaryResponse:
    """Retrieve risk severity vs intervention priority landscape, driver taxonomy, and sensitivity proof."""
    service = RiskService(repo)
    return service.get_risk_summary(filters)


@router.get("/priorities", response_model=List[PrioritySchoolItem], summary="Get intervention priority queue")
def get_priorities(
    filters: Dict[str, Any] = Depends(get_filter_params),
    limit: int = Query(50, ge=1, le=600, description="Max records to return"),
    repo: DuckDBRepository = Depends(get_repository),
) -> List[PrioritySchoolItem]:
    """Retrieve ranked queue of schools requiring administrative intervention review."""
    service = RiskService(repo)
    return service.get_priorities_table(filters, limit=limit)


@router.get("/drivers", response_model=List[DriverDistributionItem], summary="Get primary driver distribution")
def get_drivers(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> List[DriverDistributionItem]:
    """Retrieve distribution of primary vulnerability drivers across schools."""
    service = RiskService(repo)
    res = service.get_risk_summary(filters)
    return res.driver_distribution
