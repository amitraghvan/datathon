"""Reusable atomic UI components for EduPulse AI."""

from typing import Optional

import streamlit as st


def render_metric_card(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    delta: Optional[str] = None,
    delta_color: str = "normal",  # "normal", "inverse", "off"
    border_accent: Optional[str] = None,
) -> None:
    """Render an executive styled KPI metric card."""
    accent_style = f"border-top: 3px solid {border_accent};" if border_accent else ""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    subtext_html = f'<div class="metric-subtext">{subtitle}</div>' if subtitle else ""

    html = f"""
    <div class="metric-card" style="{accent_style}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
        {subtext_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: Optional[str] = None, badge_text: Optional[str] = None, badge_variant: str = "neutral") -> None:
    """Render a clean, consulting-grade section header with optional subtitle and badge."""
    badge_html = f'<span class="badge badge-{badge_variant}">{badge_text}</span>' if badge_text else ""
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""

    html = f"""
    <div class="section-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 class="section-title">{title}</h2>
            {badge_html}
        </div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_badge(text: str, variant: str = "neutral") -> str:
    """Generate HTML for a semantic status badge."""
    variant_clean = variant.lower()
    return f'<span class="badge badge-{variant_clean}">{text}</span>'

def render_empty_state(title: str, message: str) -> None:
    """Render a friendly, structured empty state without raw tracebacks."""
    html = f"""
    <div style="text-align: center; padding: 3rem 1rem; background: rgba(21, 29, 46, 0.5); border: 1px dashed #2A364F; border-radius: 8px; margin: 1rem 0;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
        <h4 style="color: #F8FAFC; margin: 0 0 0.5rem 0;">{title}</h4>
        <p style="color: #94A3B8; font-size: 0.85rem; max-width: 500px; margin: 0 auto;">{message}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_data_lineage_card(
    metric_name: str,
    formula: str,
    source_table: str,
    filters_applied: str,
    exclusions: str,
    aggregation_policy: str,
) -> None:
    """Render a data governance contract card displaying end-to-end lineage."""
    html = f"""
    <div style="background: #151D2E; border: 1px solid #2A364F; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <h4 style="margin: 0; color: #38BDF8; font-size: 1rem;">📊 {metric_name}</h4>
            <span class="badge badge-low">Governed KPI</span>
        </div>
        <div style="font-family: monospace; background: #0B0F19; padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.8rem; color: #F8FAFC; margin-bottom: 0.75rem; border: 1px solid #1E293B;">
            {formula}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.8rem;">
            <div><span style="color: #64748B;">Source Table/View:</span> <strong style="color: #F8FAFC;">{source_table}</strong></div>
            <div><span style="color: #64748B;">Aggregation Policy:</span> <strong style="color: #F8FAFC;">{aggregation_policy}</strong></div>
            <div><span style="color: #64748B;">Filters:</span> <span style="color: #94A3B8;">{filters_applied}</span></div>
            <div><span style="color: #64748B;">Quarantines:</span> <span style="color: #FCA5A5;">{exclusions}</span></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
