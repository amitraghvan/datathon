"""Schemas for School 360 and School Directory."""

from typing import Dict, Optional

from pydantic import BaseModel


class AmenityStatusMap(BaseModel):
    """Five core infrastructure amenities supporting strictly TRUE, FALSE, and UNKNOWN."""

    electricity: Optional[bool] = None
    drinking_water: Optional[bool] = None
    functional_toilet: Optional[bool] = None
    boundary_wall: Optional[bool] = None
    playground: Optional[bool] = None


class SchoolSummaryItem(BaseModel):
    """Enriched school record."""

    school_id: str
    school_name: str
    district: str
    block: str
    school_type: str
    medium: str
    enrollment: int
    attendance_rate_pct: float
    academic_score: float
    student_teacher_ratio: float
    infrastructure_readiness_pct: float
    risk_score: float
    risk_tier: str
    primary_driver: str
    secondary_driver: str
    intervention_priority_score: float
    intervention_priority_tier: str
    welfare_quadrant: str
    data_quality_rate_pct: float


class SchoolProfileResponse(BaseModel):
    """Complete School 360 decision intelligence profile."""

    school_id: str
    school_name: str
    district: str
    block: str
    school_type: str
    medium: str
    enrollment: int
    student_teacher_ratio: float

    # Core performance metrics
    attendance_rate_pct: float
    academic_score: float
    infrastructure_readiness_pct: float
    risk_score: float
    risk_tier: str
    intervention_priority_score: float
    intervention_priority_tier: str
    welfare_quadrant: str
    quadrant_action: Optional[str] = None

    # Risk & Driver explanation
    primary_driver: str
    secondary_driver: str
    attendance_deficit: float
    academic_deficit: float
    infrastructure_deficit: float
    data_coverage_score: float
    confidence_score: float

    # Amenities
    amenities: AmenityStatusMap
    amenities_available_count: Optional[int] = 0
    amenities_reported_count: Optional[int] = 0

    # Deterministic recommendation
    recommended_action: str
    recommendation_details: str

    # District context comparison
    district_benchmark: Dict[str, float]


class AttendanceTimeseriesPoint(BaseModel):
    """Daily attendance observation point."""

    date: str
    present: int
    total: int
    attendance_pct: float
    records_count: int
    has_flagged_record: bool
    has_proxy_record: bool


class AssessmentSubjectItem(BaseModel):
    """FLN assessment performance by subject and grade."""

    subject: str
    grade: int
    avg_score: float
    assessment_count: int
    avg_total_marks: float
    has_proxy_score: bool


class SchoolProcurementSummary(BaseModel):
    """Procurement summary for a single school."""

    school_id: str
    school_name: str
    district: str
    total_spend_inr: float
    total_quantity_kg: float
    procurement_records: int
    avg_cost_per_kg: float
    avg_cost_per_student: float
    grain_count: int
    vendor_count: int
    is_procurement_outlier: bool
    procurement_anomaly_reason: Optional[str] = None
    spend_per_student_iqr_threshold: Optional[float] = None
