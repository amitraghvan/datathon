"""Mid-Day Meal Procurement Intelligence endpoints."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_filter_params, get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.procurement import (
    ProcurementAnomalyItem,
    ProcurementOverviewResponse,
)
from backend.app.services.procurement_service import ProcurementService

router = APIRouter()


@router.get("/overview", response_model=ProcurementOverviewResponse, summary="Get procurement spend and delivery overview")
def get_procurement_overview(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> ProcurementOverviewResponse:
    """Retrieve aggregate procurement spend, grain volume, and peer benchmark distributions."""
    service = ProcurementService(repo)
    return service.get_procurement_overview(filters)


@router.get("/anomalies", response_model=List[ProcurementAnomalyItem], summary="Get peer benchmark exception schools")
def get_procurement_anomalies(
    filters: Dict[str, Any] = Depends(get_filter_params),
    repo: DuckDBRepository = Depends(get_repository),
) -> List[ProcurementAnomalyItem]:
    """Retrieve schools flagged for per-student spend exceeding 75th percentile + 1.5 IQR."""
    service = ProcurementService(repo)
    res = service.get_procurement_overview(filters)
    return res.anomalies
