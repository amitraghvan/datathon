"""Data Trust, Lineage, and Governance endpoints."""

from typing import List

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.quality import (
    MetricLineageItem,
    QualitySummaryResponse,
)
from backend.app.services.quality_service import QualityService

router = APIRouter()


@router.get("/summary", response_model=QualitySummaryResponse, summary="Get data quality trust overview and 10 quality gates")
def get_quality_summary(repo: DuckDBRepository = Depends(get_repository)) -> QualitySummaryResponse:
    """Retrieve master data trust score (94.6/100), 10 quality gates checklist, and dataset reconciliation matrix."""
    service = QualityService(repo)
    return service.get_quality_summary()


@router.get("/lineage", response_model=List[MetricLineageItem], summary="Get governed KPI lineage contracts")
def get_quality_lineage(repo: DuckDBRepository = Depends(get_repository)) -> List[MetricLineageItem]:
    """Retrieve end-to-end data lineage contracts for core governed metrics."""
    service = QualityService(repo)
    res = service.get_quality_summary()
    return res.lineage_catalog
