"""Master Application Entry Point for EduPulse AI — Education Welfare Command Center.

Enterprise decision intelligence platform for Track 4: Education & EdTech.
Coordinates the executive UI design system, data access layer, and domain pages.
"""

import sys
from pathlib import Path

# Ensure root workspace is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.pages import (
    render_ai_analyst_preview_page,
    render_data_quality_page,
    render_executive_page,
    render_procurement_page,
    render_risk_page,
    render_school_360_page,
    render_welfare_page,
)
from src.ui import (
    inject_custom_theme,
    render_app_header,
    render_global_filter_bar,
)

# Configure page settings
st.set_page_config(
    page_title="EduPulse AI — Education Welfare Command Center",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)



def main() -> None:
    """Master application controller."""
    # 1. Inject consulting-grade dark theme CSS
    inject_custom_theme()

    # 2. Render global header banner and navigation
    current_page = render_app_header()

    # 3. Render global cascading filter strip
    active_filters = render_global_filter_bar()

    # 4. Route to selected page module
    if current_page == "Executive Overview":
        render_executive_page(active_filters)
    elif current_page == "School 360":
        render_school_360_page(active_filters)
    elif current_page == "Welfare & Infrastructure":
        render_welfare_page(active_filters)
    elif current_page == "Mid-Day Meals":
        render_procurement_page(active_filters)
    elif current_page == "Risk & Intervention":
        render_risk_page(active_filters)
    elif current_page == "Data Trust & Governance":
        render_data_quality_page(active_filters)
    elif current_page == "AI Analyst (Phase 6 Preview)":
        render_ai_analyst_preview_page(active_filters)
    else:
        render_executive_page(active_filters)

    # 5. Executive Footer
    st.markdown("""
    <div style="margin-top: 3rem; padding: 1.5rem 0; border-top: 1px solid #2A364F; text-align: center; font-size: 0.75rem; color: #64748B;">
        <strong>EDUPULSE AI</strong> &nbsp;|&nbsp; Education Welfare Command Center &nbsp;|&nbsp; TransOrg AgentIQ Datathon Track 4 &nbsp;|&nbsp; Master Data Trust Score: <strong>94.6 / 100</strong>
        <br/>
        <em>Powered by DuckDB Vectorized Analytics, Star-Schema Warehouse, and Explainable Multi-Factor Risk Intelligence</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
