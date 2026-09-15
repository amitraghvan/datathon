import sys
from pathlib import Path
from typing import Any, Dict

# Bootstrap workspace root for standalone execution
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui.components import render_section_header


def render_ai_analyst_preview_page(filters: Dict[str, Any]) -> None:
    """Render preview card for Phase 6 Graph-First AI Analyst."""
    render_section_header(
        title="Graph-First Decision AI Analyst (Phase 6 Preview)",
        subtitle="Conversational decision intelligence and automated administrative briefings",
        badge_text="Upcoming Phase 6",
        badge_variant="moderate",
    )

    st.markdown("""
    <div style="background: linear-gradient(135deg, #151D2E 0%, #0F172A 100%); border: 1px solid #0284C7; border-radius: 8px; padding: 2rem; margin-top: 1rem;">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">🤖 ➔ 📊</div>
        <h3 style="color: #F8FAFC; margin: 0 0 0.5rem 0;">Enterprise Graph-First AI Agent (Phase 6 Architecture)</h3>
        <p style="color: #94A3B8; font-size: 0.9rem; max-width: 750px; line-height: 1.6;">
            The foundation of any trustworthy AI agent is clean data, governed dimensional models, and explainable risk scores.
            Having solidified Phases 0–5 (Data Rescue, Canonical Star Schema, Governed SQL Marts, and Executive Product UI),
            the <strong>EduPulse AI Agent</strong> in Phase 6 will provide conversational decision support with strict safety guardrails.
        </p>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem;">
            <div style="background: #0B0F19; padding: 1rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #38BDF8; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">1. Governed Tool Calls</div>
                <div style="color: #94A3B8; font-size: 0.8rem;">Agent exclusively queries compiled DuckDB views (school_risk, procurement_summary); never generates unconstrained ad-hoc SQL.</div>
            </div>
            <div style="background: #0B0F19; padding: 1rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #10B981; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">2. Anti-Hallucination</div>
                <div style="color: #94A3B8; font-size: 0.8rem;">Every claim is cited with sample sizes, exact p-values, and data coverage indicators. Disclaimers enforced automatically.</div>
            </div>
            <div style="background: #0B0F19; padding: 1rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #F59E0B; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">3. Briefing Generator</div>
                <div style="color: #94A3B8; font-size: 0.8rem;">One-click generation of exportable administrative memos for District Education Officers and inspection taskforces.</div>
            </div>
        </div>

        <div style="margin-top: 1.5rem; background: rgba(2, 132, 199, 0.1); border-left: 4px solid #0284C7; padding: 0.75rem 1rem; border-radius: 0 4px 4px 0; font-size: 0.85rem; color: #F8FAFC;">
            📌 <em>Scheduled for Phase 6 following completion and verification of the Phase 5 Executive Dashboard.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from src.ui import inject_custom_theme, render_app_header, render_global_filter_bar
    inject_custom_theme()
    render_app_header()
    filters = render_global_filter_bar()
    render_ai_analyst_preview_page(filters)
