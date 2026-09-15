"""Unit tests for Dynamic Visualization Planning."""

from src.agent.graph.intent_schema import AgentIntent, IntentType
from src.agent.grounding.evidence import EvidencePackage
from src.agent.visualization.chart_planner import plan_chart_intent


def test_chart_selection_district_benchmark():
    """Verify district benchmarking intent yields a bar chart."""
    intent = AgentIntent(intent_type=IntentType.RANKING, entity="district", metric="attendance_rate_pct")
    evidence = EvidencePackage(
        records=[{"district": "Jalandhar", "avg_attendance_rate": 79.1, "avg_academic_score": 66.5}],
        sample_size=1,
    )
    chart_plan = plan_chart_intent(intent, evidence)
    assert chart_plan.chart_type == "bar"
    assert chart_plan.is_renderable is True


def test_chart_selection_priority_ranking():
    """Verify intervention priority ranking intent yields a horizontal bar chart."""
    intent = AgentIntent(intent_type=IntentType.RANKING, entity="school", metric="intervention_priority")
    evidence = EvidencePackage(
        records=[{"school_id": "SCH0386", "district": "Bathinda", "intervention_priority_score": 88.5}],
        sample_size=1,
    )
    chart_plan = plan_chart_intent(intent, evidence)
    assert chart_plan.chart_type == "horizontal_bar"


def test_chart_selection_scatter():
    """Verify statistical association yields a scatter plot."""
    intent = AgentIntent(intent_type=IntentType.ASSOCIATION, entity="school", metric="attendance_academic_correlation")
    evidence = EvidencePackage(
        records=[{"school_id": "SCH0001", "attendance_rate_pct": 75.0, "academic_score": 60.0}],
        sample_size=1,
    )
    chart_plan = plan_chart_intent(intent, evidence)
    assert chart_plan.chart_type == "scatter"


def test_chart_selection_kpi_for_school():
    """Verify single school lookup yields a KPI scorecard."""
    intent = AgentIntent(intent_type=IntentType.LOOKUP, entity="school", metric="intervention_priority")
    evidence = EvidencePackage(
        records=[{"school_id": "SCH0386", "district": "Bathinda", "intervention_priority_score": 88.5, "attendance_rate_pct": 65.0, "academic_score": 52.0}],
        sample_size=1,
    )
    chart_plan = plan_chart_intent(intent, evidence)
    assert chart_plan.chart_type == "kpi"
