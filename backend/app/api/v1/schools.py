"""School Directory and School 360 profiling endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import get_filter_params, get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.common import DimensionOptionsResponse
from backend.app.schemas.school import (
    AmenityStatusMap,
    AssessmentSubjectItem,
    AttendanceTimeseriesPoint,
    SchoolProcurementSummary,
    SchoolProfileResponse,
    SchoolSummaryItem,
)
from backend.app.services.school_service import SchoolService
from backend.app.utils.pagination import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SchoolSummaryItem], summary="List and search schools")
def get_schools(
    filters: Dict[str, Any] = Depends(get_filter_params),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or school ID"),
    sort_by: str = Query("intervention_priority_score", description="Column to sort by"),
    sort_desc: bool = Query(True, description="Descending order if true"),
    repo: DuckDBRepository = Depends(get_repository),
) -> PaginatedResponse[SchoolSummaryItem]:
    """Retrieve filtered, paginated list of canonical schools."""
    service = SchoolService(repo)
    return service.get_schools(
        filters=filters,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )


@router.get("/dimensions", response_model=DimensionOptionsResponse, summary="Get cascading filter options")
def get_dimension_options(repo: DuckDBRepository = Depends(get_repository)) -> DimensionOptionsResponse:
    """Retrieve distinct options for cascading dropdowns."""
    service = SchoolService(repo)
    return service.get_dimension_options()


@router.get("/{school_id}", response_model=SchoolProfileResponse, summary="Get School 360 decision profile")
def get_school_profile(school_id: str, repo: DuckDBRepository = Depends(get_repository)) -> SchoolProfileResponse:
    """Retrieve complete decision intelligence profile for a single school."""
    service = SchoolService(repo)
    return service.get_school_profile(school_id)


@router.get("/{school_id}/attendance", response_model=List[AttendanceTimeseriesPoint], summary="Get attendance daily timeseries")
def get_school_attendance(school_id: str, repo: DuckDBRepository = Depends(get_repository)) -> List[AttendanceTimeseriesPoint]:
    """Retrieve daily attendance time-series observations."""
    service = SchoolService(repo)
    return service.get_school_attendance_timeseries(school_id)


@router.get("/{school_id}/academics", response_model=List[AssessmentSubjectItem], summary="Get FLN assessment scores")
def get_school_academics(school_id: str, repo: DuckDBRepository = Depends(get_repository)) -> List[AssessmentSubjectItem]:
    """Retrieve subject and grade level test performance."""
    service = SchoolService(repo)
    return service.get_school_academics(school_id)


@router.get("/{school_id}/infrastructure", response_model=AmenityStatusMap, summary="Get school amenity status")
def get_school_infrastructure(school_id: str, repo: DuckDBRepository = Depends(get_repository)) -> AmenityStatusMap:
    """Retrieve 5 core amenity statuses strictly respecting TRUE, FALSE, UNKNOWN."""
    service = SchoolService(repo)
    profile = service.get_school_profile(school_id)
    return profile.amenities


@router.get("/{school_id}/procurement", response_model=Optional[SchoolProcurementSummary], summary="Get school procurement summary")
def get_school_procurement(school_id: str, repo: DuckDBRepository = Depends(get_repository)) -> Optional[SchoolProcurementSummary]:
    """Retrieve MDM procurement spend and volume for a single school."""
    service = SchoolService(repo)
    return service.get_school_procurement(school_id)
