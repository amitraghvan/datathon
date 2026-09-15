"""School 360 Deep-Dive page for EduPulse AI.

Provides a 360-degree operational profile for any selected school:
- Header Profile Card (Name, ID, District, Block, Enrollment, School Type)
- Core Performance KPIs
- Daily Attendance Observation History with Quarantined Anomaly Flags
- FLN Academic Outcome Breakdown by Subject
- 5 Basic Amenity Cards (explicitly preserving UNKNOWN != FALSE)
- Mid-Day Meal Procurement Volume & Unit Economics
- Transparent Risk & Driver Decomposition vs. District Peers
- Deterministic Recommended Intervention Action
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Bootstrap workspace root for standalone execution
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import plotly.express as px
import streamlit as st

from src.analytics.risk import get_recommended_intervention
from src.data_access.repository import (
    get_all_schools_enriched,
    get_procurement_summary,
    get_school_assessments,
    get_school_attendance_timeseries,
    get_school_profile,
)
from src.ui.cards import (
    render_amenity_status_cards,
    render_intervention_decision_panel,
    render_school_profile_header,
)
from src.ui.charts import chart_school_attendance_timeseries
from src.ui.components import (
    render_empty_state,
    render_metric_card,
    render_section_header,
)
from src.ui.formatting import (
    format_gap,
    format_inr,
    format_kg,
    format_percent,
)


def render_school_360_page(filters: Dict[str, Any]) -> None:
    """Render the School 360 Deep-Dive profile page."""
    df_all = get_all_schools_enriched()

    # 1. School Selector
    school_list = df_all[["school_id", "school_name", "district"]].copy()
    school_list["label"] = school_list["school_id"] + " — " + school_list["school_name"] + " (" + school_list["district"] + ")"
    options = school_list["label"].tolist()

    default_idx = 0
    if "selected_school_id" in st.session_state:
        target_sid = st.session_state["selected_school_id"]
        matches = school_list[school_list["school_id"] == target_sid]
        if not matches.empty:
            target_label = matches.iloc[0]["label"]
            if target_label in options:
                default_idx = options.index(target_label)

    c_sel, c_quick = st.columns([3, 1])
    with c_sel:
        selected_label = st.selectbox(
            "Select School for 360° Profile Review:",
            options=options,
            index=default_idx,
            key="school_360_selector",
        )
    with c_quick:
        # Quick jump to top priority school
        if st.button("🚨 Jump to #1 Priority School", use_container_width=True):
            top_sid = df_all.sort_values(by="intervention_priority_score", ascending=False).iloc[0]["school_id"]
            st.session_state["selected_school_id"] = top_sid
            st.rerun()

    selected_sid = selected_label.split(" — ")[0]
    st.session_state["selected_school_id"] = selected_sid

    school = get_school_profile(selected_sid)
    if not school:
        render_empty_state("School Not Found", f"No record found for School ID: {selected_sid}")
        return

    # 2. Master Profile Header Banner
    render_school_profile_header(school)

    # 3. 4 Core School Performance Cards
    p_cols = st.columns(4)
    with p_cols[0]:
        render_metric_card(
            title="Attendance Rate",
            value=format_percent(school.get("attendance_rate")),
            subtitle=f"{school.get('attendance_records', 0)} trusted records",
            delta=format_gap(school.get("attendance_gap_vs_district")),
            border_accent="#0284C7",
        )
    with p_cols[1]:
        render_metric_card(
            title="Academic FLN Score",
            value=format_percent(school.get("academic_score")),
            subtitle=f"{school.get('assessment_records', 0)} tests administered",
            delta=format_gap(school.get("academic_gap_vs_district")),
            border_accent="#10B981" if school.get("academic_score", 0) >= 65 else "#F59E0B",
        )
    with p_cols[2]:
        render_metric_card(
            title="Infrastructure Readiness",
            value=format_percent(school.get("infrastructure_readiness_pct")),
            subtitle=f"Quadrant: {school.get('welfare_quadrant', 'N/A')}",
            delta=format_gap(school.get("infrastructure_gap_vs_district")),
            border_accent="#F59E0B" if school.get("infrastructure_readiness_pct", 0) < 50 else "#10B981",
        )
    with p_cols[3]:
        prio_score = school.get("intervention_priority_score", 0.0)
        prio_rank = school.get("intervention_rank", 0)
        render_metric_card(
            title="Intervention Priority",
            value=f"{prio_score:.1f}",
            subtitle=f"State Rank: #{prio_rank} of 600",
            border_accent="#EF4444" if prio_score >= 38 else "#0284C7",
        )

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 4. Section: Risk Decomposition & Recommended Intervention Action
    render_section_header(
        title="Intervention Intelligence & Root-Cause Explanation",
        subtitle="Decomposing risk drivers and district peer gaps to inform administrative action",
        badge_text="Decision Intelligence",
        badge_variant="high",
    )
    rec_action = get_recommended_intervention(
        school.get("risk_level", "LOW"),
        school.get("primary_risk_driver", "INFRASTRUCTURE"),
    )
    render_intervention_decision_panel(school, rec_action)

    # 5. Section: Infrastructure Amenities (Strictly preserving UNKNOWN != FALSE)
    render_section_header(
        title="Physical Infrastructure & Amenities Audit",
        subtitle="5 Basic welfare amenities evaluated from verified inspection logs",
        badge_text="Facility Audit",
        badge_variant="neutral",
    )
    render_amenity_status_cards(school)
    if school.get("latest_remarks"):
        st.markdown(
            f"<div style='font-size: 0.8rem; color: #94A3B8; margin-top: 0.5rem; background: #151D2E; padding: 0.5rem 0.8rem; border-radius: 4px; border: 1px solid #2A364F;'>"
            f"📝 <strong>Inspector Remark:</strong> <em>{school['latest_remarks']}</em></div>",
            unsafe_allow_html=True,
        )

    # 6. Section: Daily Attendance History & Academic Assessment Breakdown
    c_att, c_acad = st.columns([1, 1])

    with c_att:
        render_section_header(
            title="Daily Attendance Trend",
            subtitle="Observations over instructional days with anomaly quarantine markers",
            badge_text="Attendance Series",
            badge_variant="moderate",
        )
        df_att_series = get_school_attendance_timeseries(selected_sid)
        if not df_att_series.empty:
            fig_att = chart_school_attendance_timeseries(df_att_series)
            st.plotly_chart(fig_att, use_container_width=True)
        else:
            render_empty_state("No Attendance Logs", "No daily records on file for this school.")

    with c_acad:
        render_section_header(
            title="Academic Performance by Subject",
            subtitle="Normalized scores across FLN assessment administrations",
            badge_text="Learning Outcomes",
            badge_variant="moderate",
        )
        df_acad = get_school_assessments(selected_sid)
        if not df_acad.empty:
            # Group by subject
            subj_agg = df_acad.groupby("subject_standard").agg(
                avg_score=("normalized_score_pct", "mean"),
                total_assessed=("total_students_assessed", "sum"),
                test_count=("assessment_id", "count"),
            ).reset_index()

            fig_subj = px.bar(
                subj_agg,
                x="subject_standard",
                y="avg_score",
                color="avg_score",
                color_continuous_scale="Blues",
                text=subj_agg["avg_score"].apply(lambda v: f"{v:.1f}%"),
                hover_data={"total_assessed": True, "test_count": True},
                labels={"subject_standard": "Subject", "avg_score": "Score (%)"},
            )
            fig_subj.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#151D2E",
                font=dict(family="Inter, sans-serif", color="#F8FAFC"),
                yaxis=dict(gridcolor="#2A364F", range=[0, 100]),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                coloraxis_showscale=False,
                height=320,
            )
            st.plotly_chart(fig_subj, use_container_width=True)
            st.caption("ℹ️ Letter-grade evaluations were mapped via documented midpoint proxies; continuous marks normalized to 0–100%.")
        else:
            render_empty_state("No Assessment Logs", "No FLN assessment records on file for this school.")

    # 7. Section: Mid-Day Meal Procurement Overview
    render_section_header(
        title="Mid-Day Meal (MDM) Nutritional Welfare & Procurement",
        subtitle="Commodity transaction totals, unit costs, and peer scale benchmarks",
        badge_text="MDM Welfare",
        badge_variant="low",
    )
    df_proc_all = get_procurement_summary()
    matched_proc = df_proc_all[df_proc_all["school_id"] == selected_sid]

    if not matched_proc.empty:
        p_row = matched_proc.iloc[0]
        pr_cols = st.columns(5)
        with pr_cols[0]:
            render_metric_card("Total Spend", format_inr(p_row["total_spend_inr"]), subtitle=f"{p_row['procurement_records']} deliveries")
        with pr_cols[1]:
            render_metric_card("Total Volume", format_kg(p_row["total_quantity_kg"]), subtitle=f"{p_row['grain_count']} grain types")
        with pr_cols[2]:
            render_metric_card("Cost / Student", format_inr(p_row["avg_cost_per_student"]), subtitle="Per enrolled pupil")
        with pr_cols[3]:
            render_metric_card("Cost / KG", f"₹{p_row['avg_cost_per_kg']:.1f}", subtitle="Weighted average")
        with pr_cols[4]:
            render_metric_card("Vendors", str(p_row["vendor_count"]), subtitle="Distinct suppliers")

        if p_row.get("is_procurement_outlier"):
            st.warning(f"⚠️ **Peer Benchmark Exception**: {p_row.get('procurement_anomaly_reason', 'Higher than peer distribution')}")
    else:
        render_empty_state("No Procurement Data", "No MDM delivery records on file for this school.")

if __name__ == "__main__":
    from src.ui import inject_custom_theme, render_app_header, render_global_filter_bar
    inject_custom_theme()
    render_app_header()
    filters = render_global_filter_bar()
    render_school_360_page(filters)

