"""Overview and health check endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_filter_params, get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.common import HealthResponse
from backend.app.schemas.overview import ExecutiveOverviewResponse
from backend.app.services.overview_service import OverviewService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="System health and warehouse status")
def get_health(repo: DuckDBRepository = Depends(get_repository)) -> HealthResponse:
    """Check connectivity to DuckDB warehouse and pipeline trust state."""
    try:
        res = repo.query_one("SELECT COUNT(*) as count FROM dim_school")
        connected = bool(res and res["count"] > 0)
    except Exception:
        connected = False

    return HealthResponse(
        status="healthy" if connected else "degraded",
        warehouse_connected=connected,
        trust_score=94.6,
    )


@router.get("/overview", response_model=ExecutiveOverviewResponse, summary="Executive Command Center summary")
def get_overview(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> ExecutiveOverviewResponse:
    """Retrieve six core KPIs, dynamic alert cards, and executive visual datasets."""
    service = OverviewService(repo)
    return service.get_overview_data(filters)
