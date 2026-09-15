"""Service for District Benchmarking."""


from backend.app.repository.duckdb import DuckDBRepository
from backend.app.repository.queries import (
    DISTRICT_SUMMARY_SQL,
    SCHOOL_MASTER_ENRICHED_SQL,
)
from backend.app.schemas.district import (
    DistrictDetailResponse,
    DistrictListResponse,
    DistrictPerformanceItem,
)
from backend.app.utils.errors import DistrictNotFoundException


class DistrictService:
    """Provides district comparisons and rankings."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def get_all_districts(self) -> DistrictListResponse:
        """Fetch all district performance records."""
        records = self.repo.query_dicts(DISTRICT_SUMMARY_SQL)
        items = [DistrictPerformanceItem(**r) for r in records]
        return DistrictListResponse(districts=items, total_districts=len(items))

    def get_district_detail(self, district_name: str) -> DistrictDetailResponse:
        """Fetch summary and all enrolled schools for a specific district."""
        sql = f"{DISTRICT_SUMMARY_SQL.replace('ORDER BY d.district ASC', '')} WHERE d.district = ?"
        record = self.repo.query_one(sql, [district_name])

        if not record:
            raise DistrictNotFoundException(district_name)

        schools_sql = f"SELECT * FROM ({SCHOOL_MASTER_ENRICHED_SQL}) WHERE district = ? ORDER BY intervention_priority_score DESC"
        schools = self.repo.query_dicts(schools_sql, [district_name])

        return DistrictDetailResponse(
            summary=DistrictPerformanceItem(**record),
            schools=schools,
        )
