"""District benchmarking endpoints."""

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_repository
from backend.app.repository.duckdb import DuckDBRepository
from backend.app.schemas.district import DistrictDetailResponse, DistrictListResponse
from backend.app.services.district_service import DistrictService

router = APIRouter()


@router.get("", response_model=DistrictListResponse, summary="List all district performance benchmarks")
def get_districts(repo: DuckDBRepository = Depends(get_repository)) -> DistrictListResponse:
    """Retrieve comparative performance benchmarks across all 9 districts."""
    service = DistrictService(repo)
    return service.get_all_districts()


@router.get("/{district}", response_model=DistrictDetailResponse, summary="Get single district details and schools")
def get_district_detail(district: str, repo: DuckDBRepository = Depends(get_repository)) -> DistrictDetailResponse:
    """Retrieve detailed district metrics and list of enrolled schools."""
    service = DistrictService(repo)
    return service.get_district_detail(district)
