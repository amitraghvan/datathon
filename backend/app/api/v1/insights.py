"""Statistical Associations and Unsupervised Insights endpoints."""

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.insights import (
    AttendanceAcademicAssociationResponse,
    SchoolSegmentationResponse,
)
from backend.app.services.insights_service import InsightsService

router = APIRouter()


@router.get("/association", response_model=AttendanceAcademicAssociationResponse, summary="Attendance-Academic correlation analysis")
def get_association(repo: DuckDBRepository = Depends(get_repository)) -> AttendanceAcademicAssociationResponse:
    """Retrieve Pearson and Spearman association coefficients between attendance and FLN test scores."""
    service = InsightsService(repo)
    return service.get_attendance_academic_association()


@router.get("/segmentation", response_model=SchoolSegmentationResponse, summary="Unsupervised K-Means school clusters")
def get_segmentation(repo: DuckDBRepository = Depends(get_repository)) -> SchoolSegmentationResponse:
    """Retrieve 4-cluster K-Means segmentation results with silhouette validation."""
    service = InsightsService(repo)
    return service.get_school_segmentation()
