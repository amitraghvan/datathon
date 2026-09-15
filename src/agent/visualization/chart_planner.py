"""Chart recommendation and data transformation engine for Agent responses.

Includes a deterministic CHART_POLICY_REGISTRY that validates and may override
LLM chart recommendations to ensure visualization governance.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from src.agent.graph.intent_schema import AgentIntent, IntentType
from src.agent.grounding.evidence import EvidencePackage

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# CHART POLICY REGISTRY — Deterministic validation of chart types
# ──────────────────────────────────────────────────────────────────────

CHART_POLICY_REGISTRY: Dict[IntentType, Set[str]] = {
    IntentType.DISTRICT_BENCHMARK: {"bar", "horizontal_bar", "table"},
    IntentType.RANKING: {"bar", "horizontal_bar", "table", "kpi"},
    IntentType.COMPARISON: {"bar", "horizontal_bar", "table"},
    IntentType.TREND: {"line", "bar", "table"},
    IntentType.BREAKDOWN: {"bar", "donut", "table"},
    IntentType.DIAGNOSIS: {"kpi", "table"},
    IntentType.ASSOCIATION: {"scatter", "table"},
    IntentType.SEGMENTATION: {"scatter", "heatmap", "table"},
    IntentType.ANOMALY: {"horizontal_bar", "scatter", "table"},
    IntentType.RECOMMENDATION: {"table", "kpi"},
    IntentType.METHODOLOGY: {"table"},
    IntentType.DATA_QUALITY: {"bar", "table", "kpi"},
    IntentType.INTERVENTION_PRIORITY_RANKING: {"horizontal_bar", "bar", "table", "kpi"},
    IntentType.ATTENDANCE_LEARNING_CORRELATION: {"scatter"},
    IntentType.MDM_ANOMALY_AUDIT: {"horizontal_bar", "bar", "table"},
    IntentType.INFRASTRUCTURE_IMPACT: {"bar", "matrix", "table"},
    IntentType.SCHOOL_DEEP_DIVE: {"kpi", "table"},
    IntentType.LOOKUP: {"kpi", "table"},
    IntentType.DATA_QUALITY_DIAGNOSTIC: {"bar", "table", "kpi"},
    IntentType.RETENTION_RISK_OVERVIEW: {"scatter", "bar", "table"},
    IntentType.GENERAL_QUESTION: {"table", "bar", "kpi"},
}


def validate_llm_chart_recommendation(
    llm_chart: Optional[str],
    intent: AgentIntent,
) -> Optional[str]:
    """Validate LLM chart recommendation against the deterministic chart policy registry.

    Returns the validated chart type if approved, or the first allowed chart type
    from the policy registry if the LLM suggestion is invalid.
    Returns None if no LLM recommendation was provided.
    """
    if not llm_chart:
        return None

    allowed = CHART_POLICY_REGISTRY.get(intent.intent_type, {"table"})
    normalized = llm_chart.strip().lower()

    if normalized in allowed:
        logger.info(f"LLM chart recommendation '{normalized}' APPROVED by policy registry.")
        return normalized

    # Override with first deterministic policy option
    default = next(iter(allowed))
    logger.info(
        f"LLM chart recommendation '{normalized}' OVERRIDDEN by policy registry. "
        f"Using '{default}' instead."
    )
    return default


@dataclass
class ChartPlan:
    """Specification for rendering visualization components in UI."""

    chart_type: str  # "bar", "horizontal_bar", "line", "scatter", "matrix", "kpi", "table"
    title: str
    subtitle: str
    x_key: str
    y_keys: List[str]
    series_labels: Dict[str, str] = field(default_factory=dict)
    color_scheme: str = "indigo"
    data: List[Dict[str, Any]] = field(default_factory=list)
    kpi_value: Optional[str] = None
    kpi_subtext: Optional[str] = None
    is_renderable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert chart plan to JSON-serializable dictionary."""
        return {
            "chart_type": self.chart_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "x_key": self.x_key,
            "y_keys": self.y_keys,
            "series_labels": self.series_labels,
            "color_scheme": self.color_scheme,
            "data": self.data,
            "kpi_value": self.kpi_value,
            "kpi_subtext": self.kpi_subtext,
            "is_renderable": self.is_renderable,
        }


def plan_chart_intent(
    intent: AgentIntent,
    evidence: EvidencePackage,
    chart_recommendation: Optional[str] = None,
) -> ChartPlan:
    """Recommend and build optimal chart configuration based on analytical intent and evidence."""
    records = evidence.records
    if not records:
        return ChartPlan(
            chart_type="table",
            title="No Records Available",
            subtitle="The query returned zero matching records to visualize.",
            x_key="",
            y_keys=[],
            data=[],
            is_renderable=False,
        )

    # Validate any explicit or LLM-suggested chart type
    recommended = chart_recommendation or intent.requested_chart
    validated_chart_type = validate_llm_chart_recommendation(recommended, intent) if recommended else None

    first_row = records[0]
    itype = intent.intent_type
    entity = intent.entity

    # 1. District Benchmarking / Comparison -> Bar Chart (or horizontal_bar / table if recommended)
    if (
        itype in [IntentType.DISTRICT_BENCHMARK, IntentType.RANKING, IntentType.COMPARISON]
        and (entity == "district" or "district" in intent.dimensions or "avg_attendance_rate" in first_row)
    ):
        chart_data = []
        for r in records[:10]:
            chart_data.append({
                "district": r.get("district", "Unknown"),
                "attendance_rate": r.get("avg_attendance_rate", r.get("mean_attendance", r.get("attendance_rate", 0.0))),
                "academic_score": r.get("avg_academic_score", r.get("mean_fln_score", r.get("fln_score", 0.0))),
                "schools": r.get("total_schools", r.get("school_count", 0)),
            })
        chart_type = validated_chart_type if validated_chart_type in ["bar", "horizontal_bar", "table"] else "bar"
        return ChartPlan(
            chart_type=chart_type,
            title="District Performance Benchmark",
            subtitle="Comparative district-level academic performance and average attendance rates",
            x_key="district",
            y_keys=["attendance_rate", "academic_score"],
            series_labels={
                "attendance_rate": "Attendance Rate (%)",
                "academic_score": "Academic / FLN Score",
            },
            color_scheme="indigo",
            data=chart_data,
        )

    # 2. Intervention Priority Queue / Ranking -> Horizontal Bar Chart
    if (
        itype in [IntentType.INTERVENTION_PRIORITY_RANKING, IntentType.RANKING]
        and entity in ["school", "intervention"]
    ):
        chart_data = []
        for r in records[:10]:
            label = f"{r.get('school_id', '')} ({r.get('district', '')})" if r.get("school_id") else r.get("school_name", "School")
            chart_data.append({
                "label": label,
                "priority_score": r.get("intervention_priority_score", 0.0),
                "risk_score": r.get("risk_score", r.get("retention_risk_score", 0.0)),
                "attendance": r.get("attendance_rate_pct", r.get("attendance_rate", 0.0)),
            })
        chart_type = validated_chart_type if validated_chart_type in ["horizontal_bar", "bar", "table"] else "horizontal_bar"
        return ChartPlan(
            chart_type=chart_type,
            title="Intervention Priority Review Queue",
            subtitle="Schools ordered by operational priority score (retention risk & welfare gap)",
            x_key="label",
            y_keys=["priority_score"],
            series_labels={"priority_score": "Intervention Priority Score"},
            color_scheme="amber",
            data=chart_data,
        )

    # 3. Attendance vs Learning Correlation / Association -> Scatter Plot
    if itype in [IntentType.ATTENDANCE_LEARNING_CORRELATION, IntentType.ASSOCIATION]:
        chart_data = []
        for r in records[:50]:  # Limit points for clean scatter rendering
            chart_data.append({
                "name": r.get("school_id", ""),
                "attendance": r.get("attendance_rate_pct", r.get("attendance_rate", 0.0)),
                "academic_score": r.get("academic_score", r.get("fln_score", 0.0)),
                "district": r.get("district", ""),
            })
        return ChartPlan(
            chart_type="scatter",
            title="Attendance Rate vs. Academic Learning Score",
            subtitle="Observational bivariate association across schools (r = 0.453)",
            x_key="attendance",
            y_keys=["academic_score"],
            series_labels={"academic_score": "Academic Score (0-100)"},
            color_scheme="emerald",
            data=chart_data,
        )

    # 4. MDM / Procurement Outliers -> Horizontal Bar / Outlier Plot
    if itype in [IntentType.MDM_ANOMALY_AUDIT, IntentType.ANOMALY] or entity == "procurement":
        chart_data = []
        for r in records[:12]:
            chart_data.append({
                "commodity": r.get("commodity", "Unknown"),
                "spend": r.get("total_spend_inr", 0.0),
                "cost_ratio": r.get("cost_variance_ratio", 1.0),
                "records": r.get("transaction_count", 0),
            })
        return ChartPlan(
            chart_type="horizontal_bar",
            title="MDM Procurement Overview & Spend Distribution",
            subtitle="Commodity spend and cost variance metrics against peer distributions",
            x_key="commodity",
            y_keys=["spend"],
            series_labels={"spend": "Total Spend (INR)"},
            color_scheme="rose",
            data=chart_data,
        )

    # 5. Infrastructure Impact / Amenities -> Bar Chart
    if itype in [IntentType.INFRASTRUCTURE_IMPACT, IntentType.BREAKDOWN]:
        chart_data = []
        for r in records[:15]:
            chart_data.append({
                "category": r.get("district", r.get("school_id", "")),
                "attendance": r.get("attendance_rate_pct", r.get("attendance_rate", 0.0)),
                "academic": r.get("academic_score", r.get("fln_score", 0.0)),
                "risk_score": r.get("risk_score", r.get("retention_risk_score", 0.0)),
            })
        return ChartPlan(
            chart_type="bar",
            title="Infrastructure & Academic Breakdown",
            subtitle="Comparative outcomes across schools and amenities (observational only)",
            x_key="category",
            y_keys=["attendance", "academic"],
            series_labels={
                "attendance": "Attendance Rate (%)",
                "academic": "Academic Score",
            },
            color_scheme="cyan",
            data=chart_data,
        )

    # 6. School Deep Dive / Lookup / Diagnosis -> KPI or Table
    if (itype in [IntentType.SCHOOL_DEEP_DIVE, IntentType.LOOKUP, IntentType.DIAGNOSIS]) and "school_id" in first_row:
        return ChartPlan(
            chart_type="kpi",
            title=f"School Profile: {first_row.get('school_id', '')}",
            subtitle=f"{first_row.get('district', '')} | Type: {first_row.get('school_type', 'General')}",
            x_key="metric",
            y_keys=["value"],
            data=[
                {"metric": "Attendance Rate", "value": f"{first_row.get('attendance_rate_pct', first_row.get('attendance_rate', 0.0)):.1f}%"},
                {"metric": "Academic Score", "value": f"{first_row.get('academic_score', first_row.get('fln_score', 0.0)):.1f}"},
                {"metric": "Retention Risk", "value": f"{first_row.get('risk_score', first_row.get('retention_risk_score', 0.0)):.1f}/100"},
                {"metric": "Intervention Priority", "value": f"{first_row.get('intervention_priority_score', 0.0):.1f}/100"},
                {"metric": "Infrastructure Readiness", "value": f"{first_row.get('infrastructure_readiness_pct', 0.0):.1f}%"},
            ],
            kpi_value=f"{first_row.get('intervention_priority_score', 0.0):.1f}",
            kpi_subtext=f"Primary Driver: {first_row.get('primary_driver', 'Standard')}",
        )

    # 7. Data Quality Diagnostics -> Bar Chart
    if itype in [IntentType.DATA_QUALITY_DIAGNOSTIC, IntentType.DATA_QUALITY]:
        chart_data = []
        for r in records[:10]:
            chart_data.append({
                "entity": r.get("district", r.get("school_id", "Unknown")),
                "quality_rate": r.get("avg_data_quality_rate", r.get("data_quality_rate", 100.0)),
            })
        return ChartPlan(
            chart_type="bar",
            title="Data Quality & Integrity Diagnostics",
            subtitle="Governed audit rates across monitored educational entities",
            x_key="entity",
            y_keys=["quality_rate"],
            series_labels={"quality_rate": "Data Quality Rate (%)"},
            color_scheme="emerald",
            data=chart_data,
        )

    # Default -> Structured Table
    return ChartPlan(
        chart_type="table",
        title="Governed Analytical Records",
        subtitle=f"Tabular view of {len(records)} query results",
        x_key=list(records[0].keys())[0] if records else "",
        y_keys=list(records[0].keys())[1:4] if records and len(records[0]) > 1 else [],
        data=records[:20],
    )
