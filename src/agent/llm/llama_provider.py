"""Llama 3.1 LLM Provider for EduPulse AI — Two-Stage Governed Architecture.

Stage 1: Natural language → Structured AgentIntent JSON (planning)
Stage 2: Verified evidence → Grounded executive narrative (synthesis)

The LLM is NEVER the source of truth. DuckDB, the metric registry, and the
deterministic query planner remain the authoritative analytical layer.

Implements:
- Pydantic validation on every LLM output
- Metric registry validation
- Bounded retry with exponential backoff
- Circuit breaker (3 consecutive failures → 60s cooldown)
- Deterministic fallback for all failure modes
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from src.agent.graph.graph import semantic_graph
from src.agent.graph.intent_schema import AgentIntent, IntentType
from src.agent.graph.metric_registry import metric_registry
from src.agent.grounding.evidence import EvidencePackage
from src.agent.llm.mock_provider import MockDeterministicProvider
from src.agent.llm.provider import LLMProvider
from src.agent.llm.system_prompts import (
    ANALYST_PLANNER_SYSTEM_PROMPT,
    ANSWER_SYNTHESIS_SYSTEM_PROMPT,
    CHART_RECOMMENDATION_PROMPT,
    build_conversation_context,
    build_evidence_context,
    build_metric_context,
)
from src.agent.planner.planner import QueryPlan

logger = logging.getLogger(__name__)

# Metric ontology context — built once at module load
_METRIC_CONTEXT = build_metric_context()


class Llama31Provider(LLMProvider):
    """Production Llama 3.1 provider with governed two-stage architecture.

    Stage 1 (Planning): User question → Llama → AgentIntent JSON → Pydantic → Metric Registry
    Stage 2 (Synthesis): Verified evidence → Llama → Grounded narrative → Claim validation

    Environment variables:
        LLAMA_API_KEY: API key (Groq, Together, etc.) — NEVER logged or exposed
        LLAMA_BASE_URL: OpenAI-compatible API base URL
        LLAMA_MODEL: Model identifier (default: llama-3.1-70b-versatile)
        LLAMA_TIMEOUT_SECONDS: Request timeout (default: 30)
        LLAMA_TEMPERATURE: Planning temperature (default: 0)
        LLAMA_MAX_TOKENS: Max response tokens (default: 2048)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.api_key = api_key or os.environ.get("LLAMA_API_KEY", "")
        self.base_url = (
            base_url
            or os.environ.get("LLAMA_BASE_URL", "https://api.groq.com/openai/v1")
        ).rstrip("/")
        self.model = model or os.environ.get("LLAMA_MODEL", "llama-3.1-70b-versatile")
        self.timeout = timeout or float(os.environ.get("LLAMA_TIMEOUT_SECONDS", "30"))
        self.temperature = temperature if temperature is not None else float(
            os.environ.get("LLAMA_TEMPERATURE", "0")
        )
        self.max_tokens = max_tokens or int(os.environ.get("LLAMA_MAX_TOKENS", "2048"))

        # Deterministic fallback — always available
        self.fallback = MockDeterministicProvider()

        # Circuit breaker state
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0
        self._max_failures_before_circuit = 3
        self._circuit_cooldown_seconds = 60.0

    @property
    def is_configured(self) -> bool:
        """Check if Llama API credentials are present."""
        return bool(self.api_key)

    @property
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        return f"llama_3.1 ({self.model})"

    @property
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is tripped."""
        if self._consecutive_failures >= self._max_failures_before_circuit:
            if time.time() < self._circuit_open_until:
                return True
            # Cooldown expired — reset circuit
            self._consecutive_failures = 0
            self._circuit_open_until = 0.0
        return False

    def _record_success(self) -> None:
        """Reset circuit breaker on successful call."""
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0

    def _record_failure(self) -> None:
        """Increment failure counter and potentially trip circuit breaker."""
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._max_failures_before_circuit:
            self._circuit_open_until = time.time() + self._circuit_cooldown_seconds
            logger.warning(
                f"Llama circuit breaker OPEN — {self._consecutive_failures} consecutive failures. "
                f"Routing to deterministic fallback for {self._circuit_cooldown_seconds}s."
            )

    def _call_chat_completions(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        max_retries: int = 2,
    ) -> Optional[str]:
        """Make synchronous HTTP call to OpenAI-compatible chat completions API.

        Implements:
        - Circuit breaker check
        - Bounded retry with exponential backoff
        - Timeout handling
        - Rate limit (429) handling
        - Authentication error handling

        NEVER logs the API key.
        """
        if not self.is_configured:
            return None

        if self.is_circuit_open:
            logger.info("Llama circuit breaker is OPEN — skipping API call.")
            return None

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        import re
                        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                    self._record_success()
                    return content

            except urllib.error.HTTPError as e:
                last_error = e
                status_code = e.code

                if status_code == 401 or status_code == 403:
                    # Auth error — don't retry, don't log the key
                    logger.error(
                        f"Llama API authentication failed (HTTP {status_code}). "
                        "Check LLAMA_API_KEY environment variable."
                    )
                    self._record_failure()
                    return None

                if status_code == 429:
                    # Rate limited — instantly fall back to deterministic engine without lag
                    logger.warning(
                        "Llama/Groq API rate limited (429). Instantly activating deterministic engine fallback."
                    )
                    self._record_failure()
                    return None

                if status_code >= 500:
                    # Server error — backoff and retry
                    backoff = min(2 ** attempt * 0.5, 5.0)
                    logger.warning(
                        f"Llama API server error (HTTP {status_code}). "
                        f"Retrying in {backoff:.1f}s (attempt {attempt + 1}/{max_retries + 1})."
                    )
                    time.sleep(backoff)
                    continue

                # Other HTTP errors — don't retry
                logger.warning(f"Llama API error (HTTP {status_code}): {e}")
                self._record_failure()
                return None

            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_error = e
                backoff = min(2 ** attempt * 0.5, 5.0)
                logger.warning(
                    f"Llama API network error: {e}. "
                    f"Retrying in {backoff:.1f}s (attempt {attempt + 1}/{max_retries + 1})."
                )
                if attempt < max_retries:
                    time.sleep(backoff)
                continue

            except Exception as e:
                last_error = e
                logger.warning(f"Unexpected Llama API error: {e}")
                self._record_failure()
                return None

        # All retries exhausted
        logger.warning(
            f"Llama API call failed after {max_retries + 1} attempts. "
            f"Last error: {last_error}. Falling back to deterministic engine."
        )
        self._record_failure()
        return None

    # ──────────────────────────────────────────────────────────────────
    # STAGE 1 — ANALYST PLANNER
    # ──────────────────────────────────────────────────────────────────

    def parse_intent(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentIntent:
        """Parse natural language query into validated AgentIntent using Llama 3.1.

        Pipeline:
        1. Always run deterministic heuristic as authoritative baseline
        2. If Llama is configured, send query + metric ontology → Llama
        3. Parse JSON response → Pydantic validation → Metric registry validation
        4. On any failure: retry once with repair prompt, then deterministic fallback
        """
        # Authoritative baseline — always available
        heuristic_intent = semantic_graph.parse_query_to_intent(query, context)

        if not self.is_configured or self.is_circuit_open:
            return heuristic_intent

        # Build conversation context for follow-up resolution
        conversation_ctx = ""
        if context:
            turns = context.get("_conversation_turns", [])
            if turns:
                conversation_ctx = build_conversation_context(turns)

        # Build messages with metric ontology
        system_content = f"{ANALYST_PLANNER_SYSTEM_PROMPT}\n\n{_METRIC_CONTEXT}"
        user_content = f"User Question: {query}"
        if conversation_ctx:
            user_content = f"{conversation_ctx}\n\n{user_content}"
        if context:
            # Inject resolved context (e.g., "there" → specific district)
            ctx_hints = {k: v for k, v in context.items() if not k.startswith("_")}
            if ctx_hints:
                user_content += f"\n\nResolved Context: {json.dumps(ctx_hints)}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

        # First attempt
        resp = self._call_chat_completions(messages, temperature=self.temperature, max_tokens=800)
        parsed_intent = self._parse_intent_json(resp, query, heuristic_intent)
        if parsed_intent:
            return parsed_intent

        # Retry with repair prompt
        if resp is not None:
            repair_messages = messages + [
                {"role": "assistant", "content": resp},
                {
                    "role": "user",
                    "content": (
                        "Your response was not valid JSON. Please respond with ONLY a valid JSON object "
                        "matching the schema described in the system prompt. No markdown, no explanation."
                    ),
                },
            ]
            repair_resp = self._call_chat_completions(
                repair_messages, temperature=0.0, max_tokens=800
            )
            parsed_intent = self._parse_intent_json(repair_resp, query, heuristic_intent)
            if parsed_intent:
                return parsed_intent

        # All LLM attempts failed — deterministic fallback
        logger.info("Llama intent parsing failed; using deterministic heuristic fallback.")
        return heuristic_intent

    def _parse_intent_json(
        self,
        raw_response: Optional[str],
        original_query: str,
        heuristic_fallback: AgentIntent,
    ) -> Optional[AgentIntent]:
        """Attempt to parse and validate a Llama JSON response into AgentIntent.

        Validation chain:
        1. Extract JSON from potential markdown wrapping
        2. Parse as dict
        3. Validate intent_type is a known IntentType
        4. Validate metric is in the canonical metric registry
        5. Build AgentIntent with Pydantic validation
        """
        if not raw_response:
            return None

        try:
            # Extract JSON from markdown code fences or surrounding text
            clean = raw_response.strip()
            import re
            clean = re.sub(r"<think>.*?</think>", "", clean, flags=re.DOTALL).strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()

            match = re.search(r"(\{.*\})", clean, re.DOTALL)
            if match:
                clean = match.group(1)

            parsed = json.loads(clean)
            if not isinstance(parsed, dict):
                return None

            # Validate intent_type
            raw_intent = parsed.get("intent_type", "")
            try:
                intent_type = IntentType(raw_intent)
            except ValueError:
                logger.warning(f"Llama returned unknown intent_type: {raw_intent}")
                return None

            # Validate metric against registry
            raw_metric = parsed.get("metric") or "intervention_priority"
            resolved_metric = metric_registry.get_metric(raw_metric)
            if not resolved_metric and raw_metric:
                # Try resolving from the heuristic
                resolved_metric = metric_registry.resolve_metric(raw_metric)
            metric_id = (
                resolved_metric.metric_id
                if resolved_metric
                else (heuristic_fallback.metric or "intervention_priority")
            )

            # Build validated intent
            filters = parsed.get("filters", {})
            if isinstance(filters, list):
                # Handle case where LLM returns list-of-dicts filter format
                filter_dict = {}
                for f in filters:
                    if isinstance(f, dict) and "field" in f and "value" in f:
                        filter_dict[f["field"]] = f["value"]
                filters = filter_dict

            return AgentIntent(
                intent_type=intent_type,
                entity=parsed.get("entity", heuristic_fallback.entity),
                metric=metric_id,
                dimensions=parsed.get("dimensions", heuristic_fallback.dimensions),
                filters=filters,
                limit=min(int(parsed.get("limit", 10)), 100),  # Cap at 100
                needs_explanation=bool(parsed.get("needs_explanation", False)),
                requested_chart=parsed.get("requested_chart"),
                raw_query=original_query,
                confidence=min(float(parsed.get("confidence", 0.9)), 1.0),
            )

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning(f"Failed to parse Llama intent JSON: {e}")
            return None

    # ──────────────────────────────────────────────────────────────────
    # STAGE 2 — ANSWER SYNTHESIS
    # ──────────────────────────────────────────────────────────────────

    def synthesize_answer(
        self,
        query: str,
        evidence: EvidencePackage,
        plan: QueryPlan,
    ) -> str:
        """Generate evidence-grounded executive narrative using Llama 3.1.

        Pipeline:
        1. Build verified evidence context (ONLY DuckDB results)
        2. Send to Llama with strict synthesis prompt
        3. Return synthesized answer (claim validation happens upstream in agent.py)
        4. On failure: deterministic fallback
        """
        if not self.is_configured or self.is_circuit_open:
            return self.fallback.synthesize_answer(query, evidence, plan)

        # Build evidence context
        evidence_ctx = build_evidence_context(
            query=query,
            intent_type=plan.intent.intent_type.value,
            primary_metric=plan.primary_metric,
            metric_label=plan.metric_meta.label,
            evidence_records=evidence.records[:15],
            methodology=plan.to_dict().get("methodology", {}),
            caveats=plan.metric_meta.caveat_list + (
                ["Strictly observational correlation"] if plan.metric_meta.is_observational_only else []
            ),
            sample_size=evidence.record_count,
        )

        messages = [
            {"role": "system", "content": ANSWER_SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": evidence_ctx},
        ]

        # Use slightly higher temperature for natural language generation
        resp = self._call_chat_completions(
            messages, temperature=0.1, max_tokens=self.max_tokens
        )

        if resp and len(resp.strip()) > 100:
            return resp.strip()

        # Fallback
        logger.info("Llama synthesis failed; using deterministic narrative fallback.")
        return self.fallback.synthesize_answer(query, evidence, plan)

    # ──────────────────────────────────────────────────────────────────
    # CHART INTELLIGENCE
    # ──────────────────────────────────────────────────────────────────

    def recommend_chart_type(
        self,
        query: str,
        intent: AgentIntent,
        record_count: int,
    ) -> Optional[str]:
        """Ask Llama to recommend a chart type for the query result.

        The recommendation is advisory only — the deterministic chart policy
        registry validates and may override the recommendation.
        """
        if not self.is_configured or self.is_circuit_open:
            return None

        user_content = (
            f"Query: {query}\n"
            f"Intent Type: {intent.intent_type.value}\n"
            f"Entity: {intent.entity}\n"
            f"Metric: {intent.metric}\n"
            f"Record Count: {record_count}\n"
            f"Dimensions: {intent.dimensions}"
        )

        messages = [
            {"role": "system", "content": CHART_RECOMMENDATION_PROMPT},
            {"role": "user", "content": user_content},
        ]

        resp = self._call_chat_completions(messages, temperature=0.0, max_tokens=20)
        if resp:
            chart_type = resp.strip().lower().replace('"', "").replace("'", "")
            valid_types = {
                "bar", "horizontal_bar", "line", "scatter", "heatmap",
                "table", "matrix", "donut", "kpi", "none",
            }
            if chart_type in valid_types:
                return chart_type
            logger.info(f"Llama suggested invalid chart type '{chart_type}'; ignoring.")

        return None

    def synthesize_with_repair(
        self,
        query: str,
        evidence: EvidencePackage,
        plan: QueryPlan,
        failed_answer: str,
        validation_issues: str,
    ) -> str:
        """Retry synthesis with a repair prompt after grounding validation failure.

        If the repair also fails validation, the caller should use the deterministic fallback.
        """
        if not self.is_configured or self.is_circuit_open:
            return self.fallback.synthesize_answer(query, evidence, plan)

        evidence_ctx = build_evidence_context(
            query=query,
            intent_type=plan.intent.intent_type.value,
            primary_metric=plan.primary_metric,
            metric_label=plan.metric_meta.label,
            evidence_records=evidence.records[:15],
            methodology=plan.to_dict().get("methodology", {}),
            caveats=plan.metric_meta.caveat_list,
            sample_size=evidence.record_count,
        )

        messages = [
            {"role": "system", "content": ANSWER_SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": evidence_ctx},
            {"role": "assistant", "content": failed_answer},
            {
                "role": "user",
                "content": (
                    f"GROUNDING VALIDATION FAILED.\n"
                    f"Issues: {validation_issues}\n\n"
                    "Rewrite your answer using ONLY the numbers, school IDs, district names, "
                    "and metric values present in the VERIFIED_DATA section above. "
                    "Do NOT introduce any facts not in the evidence."
                ),
            },
        ]

        resp = self._call_chat_completions(messages, temperature=0.0, max_tokens=self.max_tokens)
        if resp and len(resp.strip()) > 100:
            return resp.strip()

        return self.fallback.synthesize_answer(query, evidence, plan)
