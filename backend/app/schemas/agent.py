"""Governed schemas for Phase 6 Graph-First AI Decision Intelligence Analyst."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    """Natural language query payload submitted by administrator."""

    query: str
    session_id: Optional[str] = None
    context_override: Optional[Dict[str, Any]] = None
    active_filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentFeedbackRequest(BaseModel):
    """Human-in-the-loop analyst feedback on agent reasoning and citations."""

    query_id: str
    helpful: bool
    comments: Optional[str] = None
    session_id: Optional[str] = None


class ConfigureLLMRequest(BaseModel):
    """Payload to configure or update the LLM provider at runtime."""

    provider: str = "llama_3.1"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None



class AgentCapabilitiesResponse(BaseModel):
    """Catalog of agent analytical capabilities, ontology, and governance guardrails."""

    supported_intents: List[str]
    governed_metrics: List[Dict[str, Any]]
    supported_districts: List[str]
    guardrails: List[str]
    architecture: str = "Semantic Graph -> Governed SQL -> DuckDB -> Evidence Validation -> Cited Synthesis"
    llm_provider: Optional[str] = None
    reasoning_mode: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Structured, evidence-grounded decision intelligence response format."""

    status: str = "success"
    query_id: str
    query: str
    intent_type: str
    confidence: float
    answer: str
    summary: str
    primary_metric: str
    primary_metric_label: str
    evidence_count: int
    evidence_records: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    chart_plan: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    methodology: Dict[str, Any] = Field(default_factory=dict)
    caveats: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    grounding_audit: Dict[str, Any] = Field(default_factory=dict)
    timings_ms: Dict[str, float] = Field(default_factory=dict)
    session_id: Optional[str] = None

    # Phase 6 LLM integration fields
    reasoning_mode: Optional[str] = "deterministic"
    llm_provider: Optional[str] = "mock_deterministic"

    # Backward compatibility fields for Phase 5 UI clients
    chart_type: Optional[str] = None
    chart_data: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 1.0
