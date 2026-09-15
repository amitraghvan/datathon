"""Domain-specific structured cards for EduPulse AI."""

from typing import Any, Dict

import streamlit as st

from src.ui.formatting import format_gap, format_number


def render_school_profile_header(school: Dict[str, Any]) -> None:
    """Render the master profile banner for a school in School 360."""
    sid = school.get("school_id", "N/A")
    name = school.get("school_name", "Unknown School")
    dist = school.get("district", "Unknown")
    block = school.get("block", "Unknown")
    enr = format_number(school.get("enrollment", 0))
    stype = school.get("school_type", "Standard")
    med = school.get("medium", "Standard")
    impute = school.get("district_imputation_status", "CONFIRMED_ORIGINAL")

    impute_badge = '<span class="badge badge-low">Verified Lineage</span>' if impute == "CONFIRMED_ORIGINAL" else '<span class="badge badge-high">Rescued via Block</span>'

    html = f"""
    <div style="background: linear-gradient(135deg, #151D2E 0%, #1E293B 100%); border: 1px solid #2A364F; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <h2 style="color: #F8FAFC; margin: 0; font-size: 1.5rem;">{name}</h2>
                    <span style="font-family: monospace; background: #0B0F19; color: #38BDF8; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.85rem; border: 1px solid #0284C7;">{sid}</span>
                    {impute_badge}
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.35rem;">
                    📍 <strong>{dist}</strong> District &nbsp;|&nbsp; Block: <strong>{block}</strong> &nbsp;|&nbsp; Medium: <strong>{med}</strong> &nbsp;|&nbsp; Type: <strong>{stype}</strong>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Total Enrollment</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #F8FAFC;">{enr}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_amenity_status_cards(school: Dict[str, Any]) -> None:
    """Render cards for the 5 basic amenities, explicitly distinguishing UNKNOWN from FALSE."""
    amenities = [
        ("Drinking Water", school.get("water_status", "UNKNOWN"), "💧"),
        ("Functional Toilet", school.get("toilet_status", "UNKNOWN"), "🚻"),
        ("Electricity", school.get("electricity_status", "UNKNOWN"), "⚡"),
        ("Boundary Wall", school.get("boundary_status", "UNKNOWN"), "🧱"),
        ("Playground", school.get("playground_status", "UNKNOWN"), "⚽"),
    ]

    cols = st.columns(5)
    for col, (name, status, icon) in zip(cols, amenities):
        with col:
            if status == "TRUE":
                badge_html = '<span style="color: #10B981; font-weight: 600; font-size: 0.85rem;">● Operational</span>'
                card_border = "#10B981"
                bg = "rgba(16, 185, 129, 0.05)"
            elif status == "FALSE":
                badge_html = '<span style="color: #EF4444; font-weight: 600; font-size: 0.85rem;">✕ Constrained</span>'
                card_border = "#EF4444"
                bg = "rgba(239, 68, 68, 0.05)"
            else:
                badge_html = '<span style="color: #F59E0B; font-weight: 600; font-size: 0.85rem;">? Uninspected</span>'
                card_border = "#F59E0B"
                bg = "rgba(245, 158, 11, 0.05)"

            html = f"""
            <div style="background: {bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 0.8rem; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                <div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.35rem;">{name}</div>
                {badge_html}
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

def render_intervention_decision_panel(school: Dict[str, Any], recommended_action: str) -> None:
    """Render a consulting-grade intervention decision card decomposing risk drivers and peer gaps."""
    prio = school.get("intervention_priority_score", 0.0)
    risk = school.get("risk_score", 0.0)
    driver = school.get("primary_risk_driver", "INFRASTRUCTURE")
    att_gap = school.get("attendance_gap_vs_district", 0.0)
    acad_gap = school.get("academic_gap_vs_district", 0.0)
    infra_gap = school.get("infrastructure_gap_vs_district", 0.0)

    html = f"""
    <div style="background: #151D2E; border: 1px solid #0284C7; border-radius: 8px; padding: 1.25rem; margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #2A364F; padding-bottom: 0.75rem;">
            <div>
                <span style="font-size: 0.75rem; text-transform: uppercase; color: #64748B; font-weight: 600;">Intervention Priority Rank</span>
                <div style="font-size: 1.4rem; font-weight: 700; color: #38BDF8;">Priority Score: {prio:.1f} / 100</div>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-high">Primary Driver: {driver}</span>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">Risk Severity: {risk:.1f}</div>
            </div>
        </div>

        <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.8rem; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 0.35rem;">Recommended Intervention Action:</div>
            <div style="background: rgba(2, 132, 199, 0.1); border-left: 4px solid #0284C7; padding: 0.75rem 1rem; border-radius: 0 4px 4px 0; color: #F8FAFC; font-weight: 500; font-size: 0.9rem;">
                🎯 {recommended_action}
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; font-size: 0.8rem; background: #0B0F19; padding: 0.75rem; border-radius: 6px; border: 1px solid #1E293B;">
            <div>
                <span style="color: #64748B;">Attendance vs District:</span><br/>
                <strong style="color: {'#EF4444' if att_gap < 0 else '#10B981'};">{format_gap(att_gap)}</strong>
            </div>
            <div>
                <span style="color: #64748B;">Academics vs District:</span><br/>
                <strong style="color: {'#EF4444' if acad_gap < 0 else '#10B981'};">{format_gap(acad_gap)}</strong>
            </div>
            <div>
                <span style="color: #64748B;">Infrastructure vs District:</span><br/>
                <strong style="color: {'#EF4444' if infra_gap < 0 else '#10B981'};">{format_gap(infra_gap)}</strong>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_insight_card(
    title: str,
    finding: str,
    evidence: str,
    interpretation: str,
    limitation: str,
) -> None:
    """Render a structured executive insight card complying with non-causal governance."""
    html = f"""
    <div style="background: #151D2E; border: 1px solid #2A364F; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h4 style="margin: 0; color: #38BDF8; font-size: 0.95rem;">💡 {title}</h4>
            <span class="badge badge-moderate">Evidence-Based Insight</span>
        </div>
        <div style="font-size: 0.9rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.5rem;">
            {finding}
        </div>
        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.5rem; background: #0B0F19; padding: 0.4rem 0.6rem; border-radius: 4px; border-left: 3px solid #0284C7;">
            <strong>Statistical Evidence:</strong> {evidence}
        </div>
        <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 0.5rem;">
            <strong>Business Interpretation:</strong> {interpretation}
        </div>
        <div style="font-size: 0.75rem; color: #F59E0B; background: rgba(245, 158, 11, 0.08); padding: 0.35rem 0.6rem; border-radius: 4px;">
            ⚠️ <strong>Analytical Limitation:</strong> {limitation}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
