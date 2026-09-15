"""Phase 6 Graph-First AI Decision Intelligence Analyst API Endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.agent import (
    AgentCapabilitiesResponse,
    AgentFeedbackRequest,
    AgentQueryRequest,
    AgentQueryResponse,
    ConfigureLLMRequest,
)
from backend.app.services.agent_service import agent_service

router = APIRouter()


@router.post(
    "/configure-llm",
    summary="Dynamically configure active LLM engine (Groq, Together, Ollama, OpenAI, or Deterministic)",
)
def configure_llm(payload: ConfigureLLMRequest) -> Dict[str, Any]:
    """Switch active LLM provider or update credentials dynamically at runtime."""
    try:
        return agent_service.configure_llm(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to configure LLM provider: {str(e)}",
        )


@router.post(
    "/query",
    response_model=AgentQueryResponse,
    summary="Submit natural language decision intelligence query",
)
def query_agent(payload: AgentQueryRequest) -> AgentQueryResponse:
    """Submit a question to the Graph-First Decision Intelligence Agent."""
    return agent_service.execute_query(payload)


@router.get(
    "/capabilities",
    response_model=AgentCapabilitiesResponse,
    summary="Get catalog of supported intents, metrics, and governance guardrails",
)
def get_capabilities() -> AgentCapabilitiesResponse:
    """Retrieve machine-readable agent capabilities and governance constraints."""
    return agent_service.get_capabilities()


@router.get(
    "/health",
    summary="Check agent and warehouse operational readiness",
)
def get_health() -> Dict[str, Any]:
    """Check agent and analytical warehouse status."""
    return agent_service.get_health()


@router.get(
    "/llm-status",
    summary="Check LLM provider status (credentials never exposed)",
)
def get_llm_status() -> Dict[str, Any]:
    """Return current LLM provider configuration status.

    SECURITY: API key is NEVER included in the response.
    """
    return agent_service.get_llm_status()


@router.post(
    "/feedback",
    summary="Submit analyst feedback on agent reasoning and citations",
)
def submit_feedback(payload: AgentFeedbackRequest) -> Dict[str, Any]:
    """Submit analyst feedback for precision tracking and continuous governance review."""
    return agent_service.record_feedback(payload)


@router.post(
    "/explain",
    response_model=AgentQueryResponse,
    summary="Direct diagnostic / explanation query for an educational entity",
)
def explain_entity(payload: AgentQueryRequest) -> AgentQueryResponse:
    """Convenience endpoint ensuring diagnostic explanation mode is activated."""
    if not payload.query.lower().startswith("explain") and not payload.query.lower().startswith("why"):
        payload.query = f"Explain the diagnostic drivers and priority status for {payload.query}"
    return agent_service.execute_query(payload)
