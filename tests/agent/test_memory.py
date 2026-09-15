"""Unit tests for Multi-Turn Session Memory and Context Resolution."""

from src.agent.agent import EduPulseAgent
from src.agent.memory.conversation import ConversationManager


def test_conversation_memory_context_resolution():
    """Verify follow-up queries resolve entity references from previous turns."""
    manager = ConversationManager()
    session = manager.get_session("test_session_unit")

    session.add_turn(
        query="Which district has the lowest attendance rate?",
        intent=None,
        answer="Jalandhar has the lowest attendance rate.",
        records=[{"district": "Jalandhar", "avg_attendance_rate": 79.1}],
    )

    context = session.resolve_context("Show me the top 5 schools there")
    assert context.get("district") == "Jalandhar"


def test_agent_multi_turn_execution():
    """Verify EduPulseAgent executes multi-turn conversational follow-ups accurately."""
    agent = EduPulseAgent()
    sess_id = "agent_e2e_session"

    r1 = agent.answer_query("Which district has the lowest attendance rate?", session_id=sess_id)
    assert r1.primary_metric == "attendance_rate_pct"

    r2 = agent.answer_query("Show me the top 5 schools there", session_id=sess_id)
    assert r2.evidence_count == 5
    assert r2.evidence_records[0].get("district") == "Jalandhar"
