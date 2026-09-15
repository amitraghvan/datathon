"""Executive UI Design System and Theme for EduPulse AI.

Provides consulting-grade dark/executive styling, semantic color tokens,
and CSS injection for high information density and visual hierarchy.
"""

import streamlit as st

# Color Palette Constants
COLOR_BG = "#0B0F19"
COLOR_SURFACE = "#151D2E"
COLOR_SURFACE_HOVER = "#1E293B"
COLOR_BORDER = "#2A364F"
COLOR_TEXT_PRIMARY = "#F8FAFC"
COLOR_TEXT_SECONDARY = "#94A3B8"
COLOR_TEXT_MUTED = "#64748B"

# Semantic Status Colors
COLOR_PRIMARY = "#0284C7"
COLOR_PRIMARY_ACCENT = "#38BDF8"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_NEUTRAL = "#6B7280"

# Quadrant Colors
COLOR_QUAD_MODEL = "#10B981"
COLOR_QUAD_RESILIENT = "#06B6D4"
COLOR_QUAD_ACADEMIC = "#F59E0B"
COLOR_QUAD_CRITICAL = "#EF4444"

CUSTOM_CSS = f"""
<style>
    /* Global Typography and Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    /* Top App Header Banner */
    .edupulse-header {{
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-bottom: 1px solid {COLOR_BORDER};
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        border-radius: 8px;
    }}
    .edupulse-title {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLOR_TEXT_PRIMARY};
        letter-spacing: -0.025em;
        margin: 0;
    }}
    .edupulse-subtitle {{
        font-size: 0.9rem;
        color: {COLOR_PRIMARY_ACCENT};
        font-weight: 500;
        margin-top: 0.25rem;
    }}
    .edupulse-tagline {{
        font-size: 0.8rem;
        color: {COLOR_TEXT_SECONDARY};
        margin-top: 0.2rem;
    }}

    /* Metric Cards */
    .metric-card {{
        background: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 1rem 1.25rem;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.2);
    }}
    .metric-card:hover {{
        border-color: {COLOR_PRIMARY};
        box-shadow: 0 4px 12px -2px rgba(2, 132, 199, 0.2);
    }}
    .metric-title {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {COLOR_TEXT_SECONDARY};
        margin-bottom: 0.25rem;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLOR_TEXT_PRIMARY};
        line-height: 1.2;
    }}
    .metric-subtext {{
        font-size: 0.75rem;
        color: {COLOR_TEXT_MUTED};
        margin-top: 0.35rem;
    }}
    .metric-delta {{
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 4px;
        letter-spacing: 0.025em;
        text-transform: uppercase;
    }}
    .badge-critical {{ background-color: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid #EF4444; }}
    .badge-high {{ background-color: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid #F59E0B; }}
    .badge-moderate {{ background-color: rgba(59, 130, 246, 0.15); color: #93C5FD; border: 1px solid #3B82F6; }}
    .badge-low {{ background-color: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid #10B981; }}
    .badge-neutral {{ background-color: rgba(100, 116, 139, 0.15); color: #CBD5E1; border: 1px solid #64748B; }}

    /* Section Headers */
    .section-header {{
        border-bottom: 1px solid {COLOR_BORDER};
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }}
    .section-title {{
        font-size: 1.2rem;
        font-weight: 600;
        color: {COLOR_TEXT_PRIMARY};
        margin: 0;
    }}
    .section-subtitle {{
        font-size: 0.8rem;
        color: {COLOR_TEXT_SECONDARY};
        margin-top: 0.2rem;
    }}

    /* Insight Banner Strip */
    .alert-strip {{
        background: rgba(2, 132, 199, 0.08);
        border-left: 4px solid {COLOR_PRIMARY};
        border-radius: 0 6px 6px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 1.25rem;
        font-size: 0.85rem;
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* Data Trust Quality Badge */
    .trust-badge {{
        background: linear-gradient(135deg, #065F46 0%, #047857 100%);
        color: #ECFDF5;
        font-weight: 600;
        padding: 0.35rem 0.8rem;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border: 1px solid #10B981;
    }}

    /* Custom Table Container */
    .table-container {{
        background: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 0.5rem;
    }}
</style>
"""

def inject_custom_theme() -> None:
    """Inject executive CSS style definitions into Streamlit session."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
