"""Pages package for EduPulse AI Streamlit application."""

from .ai_analyst import render_ai_analyst_preview_page
from .data_quality import render_data_quality_page
from .executive import render_executive_page
from .procurement import render_procurement_page
from .risk import render_risk_page
from .school_360 import render_school_360_page
from .welfare import render_welfare_page

__all__ = [
    "render_executive_page",
    "render_school_360_page",
    "render_welfare_page",
    "render_procurement_page",
    "render_risk_page",
    "render_data_quality_page",
    "render_ai_analyst_preview_page",
]
