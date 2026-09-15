"""Security and prompt injection defense module for EduPulse AI Agent."""

from src.agent.security.injection_guard import InjectionCheckResult, sanitize_and_check_injection

__all__ = ["InjectionCheckResult", "sanitize_and_check_injection"]
