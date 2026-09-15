"""Bounded multi-turn session memory for contextual follow-up query resolution."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.agent.graph.intent_schema import AgentIntent


@dataclass
class ConversationTurn:
    """Individual interaction turn in an agent conversation."""

    turn_id: int
    query: str
    intent: Optional[AgentIntent]
    answer: str
    primary_metric: Optional[str] = None
    district: Optional[str] = None
    school_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class ConversationSession:
    """Bounded session state tracking context across turns."""

    def __init__(self, session_id: str, max_turns: int = 10):
        self.session_id = session_id
        self.max_turns = max_turns
        self.turns: List[ConversationTurn] = []
        self.active_context: Dict[str, Any] = {
            "last_district": None,
            "last_school_id": None,
            "last_metric": None,
            "last_intent_type": None,
        }

    def add_turn(
        self,
        query: str,
        intent: Optional[AgentIntent],
        answer: str,
        primary_metric: Optional[str] = None,
        records: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Record turn and update conversational memory context."""
        turn_id = len(self.turns) + 1
        district = (
            (intent.entities.get("district") if intent and hasattr(intent, "entities") else None)
            or (intent.filters.get("district") if intent and hasattr(intent, "filters") else None)
        )
        school_id = (
            (intent.entities.get("school_id") if intent and hasattr(intent, "entities") else None)
            or (intent.filters.get("school_id") if intent and hasattr(intent, "filters") else None)
        )

        # Infer entity from top executed record if not in explicit filters
        if not district and records and len(records) > 0 and records[0].get("district"):
            district = records[0].get("district")
        if not school_id and records and len(records) > 0 and records[0].get("school_id"):
            school_id = records[0].get("school_id")

        # Update active context if present
        if district:
            self.active_context["last_district"] = district
        if school_id:
            self.active_context["last_school_id"] = school_id
        if primary_metric:
            self.active_context["last_metric"] = primary_metric
        if intent:
            self.active_context["last_intent_type"] = intent.intent_type.value

        turn = ConversationTurn(
            turn_id=turn_id,
            query=query,
            intent=intent,
            answer=answer,
            primary_metric=primary_metric,
            district=district,
            school_id=school_id,
        )
        self.turns.append(turn)

        # Enforce bounded size
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def resolve_context(self, query: str) -> Dict[str, Any]:
        """Inject context for pronoun / follow-up queries."""
        q_lower = query.lower()
        injected = {}

        # Deictic references: "there", "in that district", "for this district"
        if any(w in q_lower for w in ["there", "that district", "this district", "in it"]):
            if self.active_context.get("last_district"):
                injected["district"] = self.active_context["last_district"]

        # School pronoun references: "its", "that school", "this school"
        if any(w in q_lower for w in ["its", "that school", "this school"]):
            if self.active_context.get("last_school_id"):
                injected["school_id"] = self.active_context["last_school_id"]

        # Metric persistence if query is comparative without specifying metric
        if any(w in q_lower for w in ["what about", "how about", "compare with", "and"]):
            if self.active_context.get("last_metric") and "attendance" not in q_lower and "fln" not in q_lower:
                injected["metric"] = self.active_context["last_metric"]

        return injected


class ConversationManager:
    """Thread-safe multi-session repository."""

    def __init__(self, max_sessions: int = 500, max_turns: int = 10):
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_sessions = max_sessions
        self.max_turns = max_turns

    def get_session(self, session_id: str) -> ConversationSession:
        """Get or create session for given session ID."""
        if session_id not in self.sessions:
            if len(self.sessions) >= self.max_sessions:
                # Evict oldest session
                oldest_key = next(iter(self.sessions))
                del self.sessions[oldest_key]
            self.sessions[session_id] = ConversationSession(session_id, self.max_turns)
        return self.sessions[session_id]

    def clear_session(self, session_id: str) -> bool:
        """Reset session history."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
