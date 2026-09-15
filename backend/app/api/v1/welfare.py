"""Welfare & Physical Infrastructure Intelligence endpoints."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_filter_params, get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.welfare import (
    ElectricityComparisonItem,
    WelfareMatrixPoint,
    WelfareOverviewResponse,
)
from backend.app.services.welfare_service import WelfareService

router = APIRouter()


@router.get("/overview", response_model=WelfareOverviewResponse, summary="Get infrastructure readiness and amenity overview")
def get_welfare_overview(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> WelfareOverviewResponse:
    """Retrieve physical infrastructure readiness, amenity breakdown, and welfare gap matrix."""
    service = WelfareService(repo)
    return service.get_welfare_overview(filters)


@router.get("/matrix", response_model=List[WelfareMatrixPoint], summary="Get 2x2 Welfare Gap Matrix points")
def get_welfare_matrix(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> List[WelfareMatrixPoint]:
    """Retrieve 2x2 Welfare Gap Matrix points."""
    service = WelfareService(repo)
    res = service.get_welfare_overview(filters)
    return res.welfare_gap_matrix


@router.get("/electricity-comparison", response_model=List[ElectricityComparisonItem], summary="Electricity comparison analysis")
def get_electricity_comparison(repo: DuckDBRepository = Depends(get_repository)) -> List[ElectricityComparisonItem]:
    """Compare test scores between schools with and without functional electricity."""
    service = WelfareService(repo)
    res = service.get_welfare_overview({})
    return res.electricity_comparison
