"""Unit tests for Intent Classification and Semantic Entity Extraction."""

from src.agent.graph.entities import resolve_entities
from src.agent.graph.graph import SemanticGraphEngine
from src.agent.graph.intent_schema import IntentType, classify_intent_heuristic


def test_classify_intent_heuristic_types():
    """Verify heuristic classification maps common queries to canonical intent types."""
    assert classify_intent_heuristic("Which district has the lowest attendance rate?") == IntentType.RANKING
    assert classify_intent_heuristic("Compare attendance rates across all districts") == IntentType.COMPARISON
    assert classify_intent_heuristic("Why is SCH0386 high priority?") == IntentType.DIAGNOSIS
    assert classify_intent_heuristic("Does student attendance correlate with FLN academic scores?") == IntentType.ASSOCIATION
    assert classify_intent_heuristic("Are there any Mid-Day Meal procurement cost outliers?") == IntentType.ANOMALY
    assert classify_intent_heuristic("Which schools belong to the Critical Intervention welfare quadrant?") == IntentType.SEGMENTATION
    assert classify_intent_heuristic("What is the data trust score and profile completeness across schools?") == IntentType.DATA_QUALITY
    assert classify_intent_heuristic("How is intervention priority score calculated?") == IntentType.METHODOLOGY


def test_resolve_entities_schools_districts():
    """Verify entity extraction normalizes school codes and identifies districts."""
    e1 = resolve_entities("Top 5 schools in Patiala with lowest attendance")
    assert "Patiala" in e1.districts
    assert e1.limit == 5

    e2 = resolve_entities("Check profile for SCH0386 and sch_126")
    assert "SCH0386" in e2.school_ids
    assert "SCH0126" in e2.school_ids


def test_semantic_graph_parse_intent():
    """Verify SemanticGraphEngine packages a fully validated AgentIntent."""
    engine = SemanticGraphEngine()
    intent = engine.parse_query_to_intent("Which district has the lowest attendance rate?")
    assert intent.entity == "district"
    assert intent.metric == "attendance_rate_pct"
    assert intent.limit >= 1
