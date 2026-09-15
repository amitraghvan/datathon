"""Global layout, top navigation, and master header for EduPulse AI."""

import streamlit as st

PAGES = [
    "Executive Overview",
    "School 360",
    "Welfare & Infrastructure",
    "Mid-Day Meals",
    "Risk & Intervention",
    "Data Trust & Governance",
    "AI Analyst (Phase 6 Preview)",
]

def render_app_header() -> str:
    """Render the master brand banner with trust score and navigation."""
    # Master Header HTML
    st.markdown("""
    <div class="edupulse-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h1 class="edupulse-title">🎓 EDUPULSE AI</h1>
                <div class="edupulse-subtitle">Education Welfare Command Center</div>
                <div class="edupulse-tagline">Clean. Connect. Detect. Explain. Act. &nbsp;|&nbsp; <em>From messy data to trusted intervention intelligence</em></div>
            </div>
            <div style="display: flex; gap: 0.75rem; align-items: center;">
                <div class="trust-badge">
                    <span>🛡️ Data Trust Score:</span>
                    <strong style="font-size: 0.95rem;">94.6 / 100</strong>
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; text-align: right;">
                    <div>State: <strong>Punjab (Track 4)</strong></div>
                    <div>Schools: <strong>600 Canonical</strong></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize current page in session state if missing
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Executive Overview"

    # Navigation Bar (Radio styled as segmented button pills)
    nav_col1, nav_col2 = st.columns([5, 1])
    with nav_col1:
        current_idx = PAGES.index(st.session_state["current_page"]) if st.session_state["current_page"] in PAGES else 0
        selected = st.radio(
            "Navigation",
            PAGES,
            index=current_idx,
            horizontal=True,
            label_visibility="collapsed",
            key="app_nav_radio",
        )
        st.session_state["current_page"] = selected

    with nav_col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    return st.session_state["current_page"]
