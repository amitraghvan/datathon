"""Caching abstractions for EduPulse AI Data Access Layer.

Wraps streamlit caching functions when running within a Streamlit execution
context, while providing transparent fallback execution when invoked from
CLI scripts, unit tests, or headless background jobs.
"""

import functools
from typing import Callable, TypeVar

T = TypeVar("T")

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def cache_data_wrapper(**kwargs) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Safe wrapper around st.cache_data with fallback to standard function."""
    if HAS_STREAMLIT:
        try:
            return st.cache_data(**kwargs)
        except Exception:
            pass
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def inner(*args, **kw):
            return fn(*args, **kw)
        return inner
    return decorator

def cache_resource_wrapper(**kwargs) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Safe wrapper around st.cache_resource with fallback to standard function."""
    if HAS_STREAMLIT:
        try:
            return st.cache_resource(**kwargs)
        except Exception:
            pass
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def inner(*args, **kw):
            return fn(*args, **kw)
        return inner
    return decorator
