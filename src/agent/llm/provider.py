"""Abstract LLM Provider interface for EduPulse AI Agent.

All LLM providers (Llama 3.1, OpenAI-compatible, Mock/Deterministic) must implement
this interface. The LLM is responsible for language understanding and synthesis ONLY.
DuckDB and the metric registry remain the authoritative sources of truth.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.agent.graph.intent_schema import AgentIntent
from src.agent.grounding.evidence import EvidencePackage
from src.agent.planner.planner import QueryPlan


class LLMProvider(ABC):
    """Abstract interface for natural language parsing and synthesis providers."""

    @abstractmethod
    def parse_intent(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentIntent:
        """Parse natural language query into validated AgentIntent."""
        pass

    @abstractmethod
    def synthesize_answer(
        self,
        query: str,
        evidence: EvidencePackage,
        plan: QueryPlan,
    ) -> str:
        """Generate evidence-grounded executive narrative from executed analytical results."""
        pass

    def recommend_chart_type(
        self,
        query: str,
        intent: AgentIntent,
        record_count: int,
    ) -> Optional[str]:
        """Optional: Recommend a chart type for the query result.

        Returns None if the provider does not support chart recommendations.
        The deterministic chart policy registry always validates and may override.
        """
        return None

    @property
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        return "base_provider"

    @property
    def is_configured(self) -> bool:
        """Check if this provider has valid credentials / configuration."""
        return False
