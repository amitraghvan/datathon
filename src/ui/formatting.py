"""Value formatting utilities for EduPulse AI UI components."""

from typing import Any

import pandas as pd


def format_number(val: Any, decimals: int = 0) -> str:
    """Format numeric values with comma thousands separators."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        f = float(val)
        if decimals == 0:
            return f"{int(round(f)):,}"
        return f"{f:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)

def format_percent(val: Any, decimals: int = 1) -> str:
    """Format fractional or 0-100 percentage values."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        f = float(val)
        return f"{f:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(val)

def format_inr(val: Any, compact: bool = False) -> str:
    """Format monetary figures in Indian Rupees (INR)."""
    if val is None or pd.isna(val):
        return "₹0"
    try:
        f = float(val)
        if compact:
            if abs(f) >= 10_000_000:
                return f"₹{f / 10_000_000:.2f} Cr"
            elif abs(f) >= 100_000:
                return f"₹{f / 100_000:.2f} L"
            elif abs(f) >= 1_000:
                return f"₹{f / 1_000:.1f} K"
        return f"₹{f:,.0f}"
    except (ValueError, TypeError):
        return f"₹{val}"

def format_kg(val: Any, decimals: int = 0) -> str:
    """Format commodity volume in kilograms."""
    if val is None or pd.isna(val):
        return "0 kg"
    try:
        f = float(val)
        if decimals == 0:
            return f"{int(round(f)):,} kg"
        return f"{f:,.{decimals}f} kg"
    except (ValueError, TypeError):
        return f"{val} kg"

def format_gap(gap: Any, decimals: int = 1) -> str:
    """Format benchmark percentage point gap with explicit + or - sign."""
    if gap is None or pd.isna(gap):
        return "0.0 pp"
    try:
        f = float(gap)
        sign = "+" if f > 0 else ""
        return f"{sign}{f:.{decimals}f} pp"
    except (ValueError, TypeError):
        return str(gap)
