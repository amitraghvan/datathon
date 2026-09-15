"""Authoritative machine-readable Metric Registry for EduPulse AI.

Every business metric is cataloged with source views, units, calculation owner,
governance caveats, causal status, and allowed visualizations.
The LLM must resolve metrics through this registry and never invent metric definitions.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetricContract(BaseModel):
    """Formal specification of a governed business metric."""

    metric_id: str
    name: str
    description: str
    business_definition: str
    source_view: str
    source_columns: List[str]
    calculation_owner: str
    unit: str
    aggregation: str
    filters_supported: List[str]
    dimensions_supported: List[str]
    time_grain_supported: List[str]
    coverage_field: Optional[str] = None
    caveats: str
    causal_status: str
    allowed_visualizations: List[str] = Field(default_factory=list)

    @property
    def label(self) -> str:
        """Human-readable display label."""
        return self.name

    @property
    def is_observational_only(self) -> bool:
        """Check if metric is strictly observational."""
        return "observational" in self.causal_status.lower()

    @property
    def caveat_list(self) -> List[str]:
        """Return caveats as a list of strings."""
        if isinstance(self.caveats, list):
            return self.caveats
        return [self.caveats] if self.caveats else []



CANONICAL_METRIC_REGISTRY: Dict[str, MetricContract] = {
    "intervention_priority": MetricContract(
        metric_id="intervention_priority",
        name="Intervention Priority",
        description="Administrative action ordering index (0-100) scheduling targeted school reviews.",
        business_definition="Composite triage sequence factoring absolute risk severity and district-relative performance gaps.",
        source_view="school_intervention_priority",
        source_columns=["intervention_priority_score", "intervention_priority_tier"],
        calculation_owner="src.analytics.risk.calculate_intervention_priority",
        unit="score_0_100",
        aggregation="ranking_only",
        filters_supported=["district", "block", "school_type", "medium", "risk_tier", "primary_driver"],
        dimensions_supported=["school", "district", "block", "driver"],
        time_grain_supported=["cohort"],
        coverage_field="data_coverage_score",
        caveats="Intervention Priority is an administrative scheduling sequence, NOT equivalent to observed Risk Severity.",
        causal_status="descriptive / administrative prioritization",
        allowed_visualizations=["horizontal_bar", "bar", "table", "kpi"],
    ),
    "risk_score": MetricContract(
        metric_id="risk_score",
        name="Risk Severity Score",
        description="Observed multi-factor vulnerability score (0-100) based on weighted deficits.",
        business_definition="R = 0.45 * Attendance Deficit + 0.35 * Academic Deficit + 0.20 * Infrastructure Deficit.",
        source_view="school_risk",
        source_columns=["risk_score", "risk_level", "primary_risk_driver"],
        calculation_owner="src.analytics.risk.calculate_school_risk",
        unit="score_0_100",
        aggregation="weighted_average",
        filters_supported=["district", "block", "school_type", "medium", "risk_tier"],
        dimensions_supported=["school", "district", "block", "driver"],
        time_grain_supported=["cohort"],
        coverage_field="confidence_score",
        caveats="0 Critical Risk schools does not imply no schools require intervention. Bands: Low (0-25), Mod (25-50), High (50-75), Crit (75-100).",
        causal_status="descriptive vulnerability index",
        allowed_visualizations=["scatter", "bar", "table", "kpi"],
    ),
    "attendance_rate_pct": MetricContract(
        metric_id="attendance_rate_pct",
        name="Student Attendance Rate",
        description="Weighted student presence percentage evaluated over a 30-day monitoring window.",
        business_definition="SUM(present_students) / SUM(enrolled_students) * 100 with non-sensical records quarantined as PROXY.",
        source_view="school_performance",
        source_columns=["attendance_rate"],
        calculation_owner="src.analytics.pipeline.calculate_school_performance",
        unit="percent",
        aggregation="weighted_average",
        filters_supported=["district", "block", "school_type", "medium"],
        dimensions_supported=["school", "district", "date"],
        time_grain_supported=["daily", "30_days", "cohort"],
        coverage_field="quality_coverage_pct",
        caveats="Quarantined records (>100% attendance or negative presence) are strictly excluded from the canonical rate.",
        causal_status="descriptive presence metric",
        allowed_visualizations=["line", "bar", "table", "kpi"],
    ),
    "academic_score": MetricContract(
        metric_id="academic_score",
        name="Foundational FLN Academic Score",
        description="Normalized learning assessment performance across Math, Science, and Language.",
        business_definition="Average percentage score normalized to 0-100 scale across evaluated grades (Grades 3-8).",
        source_view="school_performance",
        source_columns=["academic_score"],
        calculation_owner="src.analytics.pipeline.calculate_school_performance",
        unit="percent",
        aggregation="average",
        filters_supported=["district", "block", "school_type", "medium", "grade", "subject"],
        dimensions_supported=["school", "district", "grade", "subject"],
        time_grain_supported=["cohort"],
        coverage_field="quality_coverage_pct",
        caveats="Assessment scales previously reported on 50/75 scales were traceably normalized to 100 in Phase 2.",
        causal_status="descriptive learning assessment",
        allowed_visualizations=["bar", "scatter", "table", "kpi"],
    ),
    "infrastructure_readiness_pct": MetricContract(
        metric_id="infrastructure_readiness_pct",
        name="Physical Infrastructure Readiness",
        description="Readiness index (0-100%) evaluating 5 statutory amenities.",
        business_definition="Weighted availability of electricity, drinking water, functional toilet, boundary wall, and playground.",
        source_view="school_welfare",
        source_columns=["infrastructure_readiness_pct", "electricity_status", "water_status", "toilet_status"],
        calculation_owner="src.analytics.pipeline.calculate_school_welfare",
        unit="percent",
        aggregation="average",
        filters_supported=["district", "block", "school_type"],
        dimensions_supported=["school", "district", "amenity"],
        time_grain_supported=["cohort"],
        coverage_field=None,
        caveats="Physical amenities strictly maintain three-valued logic: AVAILABLE, MISSING, UNKNOWN. UNKNOWN is never coerced to FALSE.",
        causal_status="descriptive physical readiness",
        allowed_visualizations=["bar", "matrix", "table", "kpi"],
    ),
    "total_spend_inr": MetricContract(
        metric_id="total_spend_inr",
        name="Mid-Day Meal Total Expenditure",
        description="Financial outlay (INR) disbursed for nutritional procurement.",
        business_definition="SUM(quantity_kg * cost_per_kg) across all delivered commodity grain receipts.",
        source_view="procurement_summary",
        source_columns=["total_spend_inr"],
        calculation_owner="src.analytics.pipeline.calculate_procurement_summary",
        unit="INR",
        aggregation="sum",
        filters_supported=["district", "commodity", "vendor"],
        dimensions_supported=["school", "district", "commodity", "vendor"],
        time_grain_supported=["monthly", "cohort"],
        coverage_field=None,
        caveats="Unit values formatted in Lakhs (₹100,000) and Crores (₹10,000,000).",
        causal_status="financial expenditure",
        allowed_visualizations=["bar", "donut", "table", "kpi"],
    ),
    "cost_per_student": MetricContract(
        metric_id="cost_per_student",
        name="Procurement Cost Per Pupil",
        description="Normalized expenditure per enrolled student in INR.",
        business_definition="total_spend_inr / enrollment.",
        source_view="procurement_summary",
        source_columns=["avg_cost_per_student"],
        calculation_owner="src.analytics.pipeline.calculate_procurement_summary",
        unit="INR_per_student",
        aggregation="average",
        filters_supported=["district"],
        dimensions_supported=["school", "district"],
        time_grain_supported=["cohort"],
        coverage_field=None,
        caveats="Outliers exceeding 1.5 IQR are classified as Peer Benchmark Exceptions, not evidence of fraud.",
        causal_status="operational unit cost",
        allowed_visualizations=["scatter", "table", "kpi"],
    ),
    "data_trust_score": MetricContract(
        metric_id="data_trust_score",
        name="Data Trust Index",
        description="Automated governance compliance score (0-100) across 10 regression quality gates.",
        business_definition="Weighted percentage of validated clean records relative to raw ingestion volume.",
        source_view="school_data_quality",
        source_columns=["data_quality_rate_pct"],
        calculation_owner="src.validation.gates.calculate_trust_score",
        unit="score_0_100",
        aggregation="weighted_average",
        filters_supported=["district"],
        dimensions_supported=["school", "district", "gate"],
        time_grain_supported=["cohort"],
        coverage_field=None,
        caveats="Current baseline is 94.6 / 100 with 10/10 quality gates passing.",
        causal_status="governance meta-indicator",
        allowed_visualizations=["table", "kpi"],
    ),
    "attendance_academic_correlation": MetricContract(
        metric_id="attendance_academic_correlation",
        name="Attendance-Academic Association",
        description="Statistical correlation between attendance rate and foundational academic scores.",
        business_definition="Pearson linear r (0.453) and Spearman rank-order rho (0.421) across 600 schools.",
        source_view="school_performance",
        source_columns=["attendance_rate", "academic_score"],
        calculation_owner="src.analytics.advanced.analyze_attendance_academic_association",
        unit="correlation_coefficient",
        aggregation="statistical_model",
        filters_supported=["district"],
        dimensions_supported=["district"],
        time_grain_supported=["cohort"],
        coverage_field="quality_coverage_pct",
        caveats="Strictly observational. Never claim that attendance causes academic improvement.",
        causal_status="observational correlation",
        allowed_visualizations=["scatter"],
    ),
}


class MetricRegistry:
    """Registry engine providing validation and discovery for all governed metrics."""

    def __init__(self) -> None:
        self.metrics = CANONICAL_METRIC_REGISTRY

    def get_metric(self, metric_id: Optional[str]) -> Optional[MetricContract]:
        if not metric_id or not isinstance(metric_id, str):
            return None
        return self.metrics.get(metric_id)

    def resolve_metric(self, phrase: Optional[str]) -> Optional[MetricContract]:
        """Resolve natural language query tokens to canonical metric contract."""
        if not phrase or not isinstance(phrase, str):
            return None
        p_lower = phrase.lower().strip()
        if not p_lower:
            return None

        # Direct ID match
        if p_lower in self.metrics:
            return self.metrics[p_lower]

        # 1. High-priority compound & statistical concepts
        if "correlat" in p_lower or "associat" in p_lower or "relat" in p_lower:
            return self.metrics["attendance_academic_correlation"]
        if "trust" in p_lower or "quality" in p_lower or "reliability" in p_lower or "completeness" in p_lower:
            return self.metrics["data_trust_score"]
        if "procurement" in p_lower or "spend" in p_lower or "meal" in p_lower or "mdm" in p_lower or "commodity" in p_lower or "cost" in p_lower:
            return self.metrics["total_spend_inr"]
        if "infrastructure" in p_lower or "infra" in p_lower or "amenity" in p_lower or "readiness" in p_lower or "electricity" in p_lower or "toilet" in p_lower or "water" in p_lower:
            return self.metrics["infrastructure_readiness_pct"]

        # 2. Risk & intervention concepts
        if "intervention" in p_lower or "priority" in p_lower or "queue" in p_lower:
            return self.metrics["intervention_priority"]
        if "risk" in p_lower or "vulnerability" in p_lower or "deficit" in p_lower:
            return self.metrics["risk_score"]

        # 3. Base performance metrics
        if "attendance" in p_lower or "present" in p_lower or "absence" in p_lower:
            return self.metrics["attendance_rate_pct"]
        if "academic" in p_lower or "fln" in p_lower or "score" in p_lower or "test" in p_lower or "learning" in p_lower:
            return self.metrics["academic_score"]

        return None

    def list_metrics(self) -> List[Dict[str, Any]]:
        return [
            {
                "metric_id": m.metric_id,
                "name": m.name,
                "description": m.description,
                "unit": m.unit,
                "source_view": m.source_view,
                "causal_status": m.causal_status,
                "caveats": m.caveats,
            }
            for m in self.metrics.values()
        ]


metric_registry = MetricRegistry()
