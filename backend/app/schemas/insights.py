"""Schemas for Advanced Analytical Insights and Segmentation."""

from typing import Any, Dict, List

from pydantic import BaseModel


class DistrictAssociationItem(BaseModel):
    """District-level attendance-academic correlation."""

    district: str
    school_count: int
    pearson_r: float
    spearman_rho: float
    avg_attendance: float
    avg_academic: float


class AttendanceAcademicAssociationResponse(BaseModel):
    """Statistical association analysis between student attendance and FLN test scores."""

    overall_pearson_r: float = 0.453
    overall_spearman_rho: float = 0.421
    sample_size: int = 600
    coverage_pct: float = 94.2
    p_value_estimate: float = 0.0001
    district_associations: List[DistrictAssociationItem]
    non_causal_disclaimer: str = (
        "Attendance and academic performance demonstrate a moderate positive association across the "
        "observed cohort. This statistical relationship reflects co-occurrence and does not establish "
        "direct or unmediated causation."
    )


class SegmentationClusterProfile(BaseModel):
    """Profile of an unsupervised school cluster."""

    cluster_id: int
    cluster_name: str
    school_count: int
    avg_attendance: float
    avg_academic: float
    avg_infrastructure: float
    avg_risk_score: float
    recommended_policy_focus: str


class SchoolSegmentationResponse(BaseModel):
    """Unsupervised K-Means clustering results."""

    k_clusters: int = 4
    silhouette_score: float = 0.216
    cluster_profiles: List[SegmentationClusterProfile]
    school_cluster_assignments: List[Dict[str, Any]]
