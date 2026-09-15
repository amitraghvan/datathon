"""Schemas for Data Trust, Lineage, and Governance."""

from typing import Any, Dict, List

from pydantic import BaseModel


class QualityGateItem(BaseModel):
    """Execution status of an individual data quality gate."""

    gate_number: int
    check_name: str
    dataset: str
    records_evaluated: int
    records_flagged: int
    resolution_method: str
    pass_status: str  # "PASS", "FLAGGED", "RESOLVED"


class MetricLineageItem(BaseModel):
    """Traceable lineage contract for a governed KPI."""

    metric_name: str
    formula: str
    source_table: str
    governed_view: str
    filters_applied: str
    exclusions: str
    aggregation_policy: str


class QualitySummaryResponse(BaseModel):
    """Complete data trust audit payload."""

    data_trust_score: float  # 94.6 / 100
    total_schools: int
    total_operational_records: int
    trusted_records: int
    flagged_records: int
    excluded_records: int
    duplicates_removed: int
    quality_gates: List[QualityGateItem]
    reconciliation_matrix: List[Dict[str, Any]]
    lineage_catalog: List[MetricLineageItem]
