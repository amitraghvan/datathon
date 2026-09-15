"""Deterministic query planner converting structured AgentIntent to governed query plans."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.agent.graph.intent_schema import AgentIntent, IntentType
from src.agent.graph.metric_registry import MetricContract, metric_registry
from src.agent.planner.sql_builder import APPROVED_VIEWS, build_filtered_query


class QueryPlan(BaseModel):
    """Execution plan containing safe SQL and metadata."""

    sql: str
    params: List[Any] = Field(default_factory=list)
    base_view: str
    metric: MetricContract
    intent: AgentIntent
    explanation_mode: bool = False
    estimated_complexity: str = "O(1)_vectorized_scan"

    @property
    def primary_metric(self) -> str:
        """Convenience property for primary metric id."""
        return self.metric.metric_id if self.metric else ""

    @property
    def metric_meta(self) -> MetricContract:
        """Convenience property for metric contract metadata."""
        return self.metric

    def to_dict(self) -> Dict[str, Any]:
        """Convert QueryPlan to dictionary."""
        return {
            "sql": self.sql,
            "params": self.params,
            "base_view": self.base_view,
            "primary_metric": self.primary_metric,
            "explanation_mode": self.explanation_mode,
            "estimated_complexity": self.estimated_complexity,
            "methodology": {
                "base_view": self.base_view,
                "metric_id": self.primary_metric,
                "complexity": self.estimated_complexity,
                "governance": "Canonical DuckDB Governed View",
            },
        }


class DeterministicQueryPlanner:
    """Deterministic compiler turning structured intent into governed query plans."""

    def __init__(self, graph: Optional[Any] = None) -> None:
        self.graph = graph
        self.registry = metric_registry

    def plan(self, intent: AgentIntent) -> QueryPlan:
        """Construct safe query plan from validated AgentIntent."""
        q_raw = intent.raw_query.lower()
        metric_contract = self.registry.get_metric(intent.metric) or self.registry.get_metric("intervention_priority")
        if not metric_contract:
            raise ValueError(f"Unknown metric {intent.metric}")

        # 1. Select base view
        if intent.entity == "district" or "district" in intent.dimensions and not intent.filters.get("school_id"):
            base_view = "district_performance"
            base_sql = APPROVED_VIEWS["district_performance"]
        elif intent.entity == "procurement" or intent.metric in ["total_spend_inr", "cost_per_student"]:
            base_view = "procurement_summary"
            base_sql = APPROVED_VIEWS["procurement_summary"]
        else:
            base_view = "school_master_enriched"
            base_sql = APPROVED_VIEWS["school_master_enriched"]

        # 2. Determine ordering column and direction
        order_col = "intervention_priority_score"
        order_dir = "DESC"

        is_ascending = any(w in q_raw for w in ["weakest", "lowest", "bottom", "poorest", "deficit", "worst", "least", "min", "minimum", "sabse kam", "kam "])

        if base_view == "district_performance":
            if intent.metric == "attendance_rate_pct":
                order_col = "avg_attendance_rate"
            elif intent.metric == "academic_score":
                order_col = "avg_academic_score"
            elif intent.metric == "infrastructure_readiness_pct":
                order_col = "avg_infrastructure_readiness"
            else:
                order_col = "avg_attendance_rate"
            order_dir = "ASC" if is_ascending else "DESC"

        elif base_view == "procurement_summary":
            order_col = "total_spend_inr"
            order_dir = "DESC"

        else:
            # school_master_enriched
            if intent.filters.get("missing_amenity"):
                order_col = "intervention_priority_score"
                order_dir = "DESC"
            elif intent.metric == "attendance_rate_pct":
                order_col = "attendance_rate_pct"
                order_dir = "ASC" if is_ascending or "low" in q_raw else "DESC"
            elif intent.metric == "academic_score":
                order_col = "academic_score"
                order_dir = "ASC" if is_ascending or "low" in q_raw else "DESC"
            elif intent.metric == "infrastructure_readiness_pct":
                order_col = "infrastructure_readiness_pct"
                order_dir = "ASC" if is_ascending or "weak" in q_raw or "poor" in q_raw else "DESC"
            elif intent.metric == "risk_score":
                order_col = "risk_score"
                order_dir = "DESC"
            elif intent.metric == "intervention_priority":
                order_col = "intervention_priority_score"
                order_dir = "DESC"

        order_by = f"{order_col} {order_dir}"

        # 3. Special intent filters & view-specific filter pruning
        active_filters = dict(intent.filters)
        if intent.intent_type == IntentType.ANOMALY and base_view == "procurement_summary":
            active_filters["is_procurement_outlier"] = True

        if "resilient" in q_raw:
            active_filters["welfare_quadrant"] = "RESILIENT"
        elif "critical quadrant" in q_raw or "welfare gap" in q_raw:
            active_filters["welfare_quadrant"] = "CRITICAL INTERVENTION"

        # Prune filters incompatible with the chosen base view
        if base_view == "district_performance":
            active_filters = {k: v for k, v in active_filters.items() if k in ["district"]}
        elif base_view == "procurement_summary":
            active_filters = {k: v for k, v in active_filters.items() if k in ["commodity", "district", "is_procurement_outlier"]}

        # 4. Generate safe parameterized SQL
        sql, params = build_filtered_query(
            base_sql=base_sql,
            filters=active_filters,
            order_by=order_by,
            limit=intent.limit,
        )

        return QueryPlan(
            sql=sql,
            params=params,
            base_view=base_view,
            metric=metric_contract,
            intent=intent,
            explanation_mode=intent.needs_explanation,
        )


query_planner = DeterministicQueryPlanner()
