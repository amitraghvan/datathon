"""Schemas for District Benchmarking."""

from typing import Any, Dict, List

from pydantic import BaseModel


class DistrictPerformanceItem(BaseModel):
    """District performance record."""

    district: str
    school_count: int
    total_enrollment: int
    avg_attendance_rate: float
    avg_academic_score: float
    avg_infrastructure_readiness: float
    avg_data_quality_rate: float
    high_priority_school_count: int
    moderate_priority_school_count: int
    critical_quadrant_school_count: int
    priority_school_rate_pct: float


class DistrictListResponse(BaseModel):
    """List of all district benchmark records."""

    districts: List[DistrictPerformanceItem]
    total_districts: int


class DistrictDetailResponse(BaseModel):
    """Detailed district profile including enrolled schools."""

    summary: DistrictPerformanceItem
    schools: List[Dict[str, Any]]
