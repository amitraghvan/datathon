"""Prompt injection detection, adversarial sanitization, and input safety guard."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class InjectionCheckResult:
    """Result of prompt injection and security validation."""

    is_safe: bool
    reason: Optional[str] = None
    sanitized_query: str = ""


# High-risk prompt injection patterns
INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
    r"(?i)\bforget\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts)\b",
    r"(?i)\bdisregard\s+(all\s+)?(safety|system|prior)\s+guidelines\b",
    r"(?i)\byou\s+are\s+now\s+(in\s+developer\s+mode|dan|unrestricted|jailbroken)\b",
    r"(?i)\b(print|reveal|output|display)\s+(your\s+)?(system\s+prompt|raw\s+instructions|hidden\s+prompt|hidden\s+instructions)\b",
    r"(?i)\b(system\s+override|admin\s+mode|root\s+access)\b",
    r"(?i)\b(drop\s+table|truncate\s+table|delete\s+from|delete\s+(all\s+)?(records|data|schools|tables?)|update\s+\w+\s+set)\b",
    r"(?i)\b(union\s+select|information_schema|sys\.tables|pragma)\b",
    r"(?i)\bread_parquet\s*\(",
    r"(?i)<\s*script[^>]*>",
    r"(?i)javascript\s*:",
]


def sanitize_and_check_injection(query: str, max_length: int = 1500) -> InjectionCheckResult:
    """Analyze query for prompt injection, adversarial payloads, and harmful commands."""
    if not query or not query.strip():
        return InjectionCheckResult(
            is_safe=False,
            reason="Empty query received.",
            sanitized_query="",
        )

    # 1. Check length
    if len(query) > max_length:
        return InjectionCheckResult(
            is_safe=False,
            reason=f"Query exceeds safe character limit ({len(query)} > {max_length}).",
            sanitized_query=query[:max_length],
        )

    # 2. Check known injection regexes
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query):
            return InjectionCheckResult(
                is_safe=False,
                reason="Adversarial prompt injection or prohibited command pattern detected.",
                sanitized_query=query,
            )

    # 3. Strip control characters
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", query).strip()

    return InjectionCheckResult(
        is_safe=True,
        reason=None,
        sanitized_query=sanitized,
    )
