"""Executive Command Center page for EduPulse AI.

The primary hero screen delivering complete situational awareness in 10 seconds:
- 6 Core Operational KPIs
- Dynamic Executive Alert Strip
- District Performance Benchmarking
- Risk Severity vs. Intervention Priority Landscape
- 2x2 Welfare Gap Matrix
- Attendance <-> Academic Association (Non-causal)
- Top Intervention Priority Action Queue
- Data Trust Pipeline Visual
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Bootstrap workspace root for standalone execution
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.data_access.repository import (
    get_district_summary,
    get_filtered_schools,
)
from src.ui.alerts import render_dynamic_alert_strip
from src.ui.charts import (
    chart_attendance_academic_association,
    chart_district_performance,
    chart_risk_vs_priority_scatter,
    chart_welfare_gap_matrix,
)
from src.ui.components import (
    render_metric_card,
    render_section_header,
)
from src.ui.formatting import (
    format_number,
    format_percent,
)
from src.ui.tables import render_priority_schools_table


def render_executive_page(filters: Dict[str, Any]) -> None:
    """Render the Executive Command Center page."""
    df_schools = get_filtered_schools(filters)
    df_dist = get_district_summary()

    if df_schools.empty:
        st.warning("No schools match the active filter criteria. Please adjust or reset filters above.")
        return

    # -------------------------------------------------------------
    # 1. 6 CORE EXECUTIVE KPIS
    # -------------------------------------------------------------
    total_schools = len(df_schools)
    avg_att = df_schools["attendance_rate"].mean()
    avg_acad = df_schools["academic_score"].mean()
    avg_infra = df_schools["infrastructure_readiness_pct"].mean()
    priority_schools_count = (df_schools["intervention_priority_score"] >= 35.0).sum()
    avg_coverage = df_schools["quality_coverage_pct"].mean()

    kpi_cols = st.columns(6)
    with kpi_cols[0]:
        render_metric_card(
            title="Schools Monitored",
            value=format_number(total_schools),
            subtitle=f"{format_number(df_schools['enrollment'].sum())} Enrolled",
            border_accent="#0284C7",
        )
    with kpi_cols[1]:
        render_metric_card(
            title="Avg Attendance",
            value=format_percent(avg_att),
            subtitle="Trusted days only",
            border_accent="#10B981" if avg_att >= 80 else "#F59E0B",
        )
    with kpi_cols[2]:
        render_metric_card(
            title="Avg FLN Academic",
            value=format_percent(avg_acad),
            subtitle="Normalized 0-100%",
            border_accent="#0284C7",
        )
    with kpi_cols[3]:
        render_metric_card(
            title="Priority Schools",
            value=format_number(priority_schools_count),
            subtitle="Priority Score ≥ 35.0",
            border_accent="#EF4444" if priority_schools_count > 0 else "#10B981",
        )
    with kpi_cols[4]:
        render_metric_card(
            title="Infra Readiness",
            value=format_percent(avg_infra),
            subtitle="5 Basic Amenities",
            border_accent="#F59E0B" if avg_infra < 60 else "#10B981",
        )
    with kpi_cols[5]:
        render_metric_card(
            title="Data Trust Coverage",
            value=format_percent(avg_coverage),
            subtitle="Valid evidence ratio",
            border_accent="#10B981",
        )

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. DYNAMIC EXECUTIVE ALERT STRIP
    # -------------------------------------------------------------
    render_dynamic_alert_strip(df_schools)

    # -------------------------------------------------------------
    # 3. SECTION 1: DISTRICT BENCHMARKING & RISK/PRIORITY LANDSCAPE
    # -------------------------------------------------------------
    c_dist, c_land = st.columns([1, 1])

    with c_dist:
        render_section_header(
            title="District Performance Benchmarking",
            subtitle="Ranked performance across administrative jurisdictions",
            badge_text="Macro View",
            badge_variant="neutral",
        )
        metric_choice = st.selectbox(
            "Select Benchmark Indicator:",
            options=[
                ("avg_attendance_rate", "Average Attendance Rate (%)"),
                ("avg_academic_score", "Average Academic Score (%)"),
                ("avg_infrastructure_readiness", "Average Infrastructure Readiness (%)"),
                ("district_risk_rate_pct", "High Priority Concentration Rate (%)"),
            ],
            format_func=lambda x: x[1],
            key="exec_dist_metric",
        )
        fig_dist = chart_district_performance(
            df_dist,
            metric_col=metric_choice[0],
            metric_label=metric_choice[1],
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with c_land:
        render_section_header(
            title="Risk Severity vs. Intervention Priority",
            subtitle="Vulnerability severity vs. operational review urgency",
            badge_text="Core Distinction",
            badge_variant="moderate",
        )
        fig_land = chart_risk_vs_priority_scatter(df_schools)
        st.plotly_chart(fig_land, use_container_width=True)

    # -------------------------------------------------------------
    # 4. SECTION 2: WELFARE GAP MATRIX & STATISTICAL ASSOCIATION
    # -------------------------------------------------------------
    c_gap, c_assoc = st.columns([1, 1])

    with c_gap:
        render_section_header(
            title="School Welfare Gap Matrix",
            subtitle="2x2 Intersection of Infrastructure (X) and Learning Outcomes (Y)",
            badge_text="Welfare Matrix",
            badge_variant="low",
        )
        fig_gap = chart_welfare_gap_matrix(df_schools)
        st.plotly_chart(fig_gap, use_container_width=True)

    with c_assoc:
        render_section_header(
            title="Attendance ↔ Academic Outcome Association",
            subtitle="Pearson r = 0.453 (p < 0.001) | Spearman rho = 0.448",
            badge_text="Non-Causal",
            badge_variant="neutral",
        )
        fig_assoc = chart_attendance_academic_association(
            df_schools,
            pearson_r=0.453,
            spearman_rho=0.448,
            sample_size=len(df_schools),
        )
        st.plotly_chart(fig_assoc, use_container_width=True)

    # -------------------------------------------------------------
    # 5. SECTION 3: TOP INTERVENTION PRIORITIES (ACTION QUEUE)
    # -------------------------------------------------------------
    render_section_header(
        title="Immediate Intervention Action Queue",
        subtitle="Ranked priority schools requiring administrative review and targeted support",
        badge_text="Actionable",
        badge_variant="high",
    )
    render_priority_schools_table(df_schools, page_size=10)

    # -------------------------------------------------------------
    # 6. SECTION 4: DATA TRUST PIPELINE
    # -------------------------------------------------------------
    render_section_header(
        title="Governed Data Trust & Lineage Architecture",
        subtitle="How messy multi-format inputs were rescued into trusted decision intelligence",
        badge_text="Data Trust",
        badge_variant="low",
    )
    st.markdown("""
    <div style="background: #151D2E; border: 1px solid #2A364F; border-radius: 8px; padding: 1.25rem; margin-top: 0.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; text-align: center; flex-wrap: wrap; gap: 0.75rem;">
            <div style="flex: 1; min-width: 120px; background: #0B0F19; padding: 0.75rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #64748B; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Step 1: Ingest</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">Raw Messy Data</div>
                <div style="color: #94A3B8; font-size: 0.75rem;">44,310 raw rows (5 sources)</div>
            </div>
            <div style="color: #0284C7; font-size: 1.2rem;">➔</div>
            <div style="flex: 1; min-width: 120px; background: #0B0F19; padding: 0.75rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #64748B; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Step 2: Rescue</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">Deterministic Rescue</div>
                <div style="color: #38BDF8; font-size: 0.75rem;">2,555 values rescued via constants</div>
            </div>
            <div style="color: #0284C7; font-size: 1.2rem;">➔</div>
            <div style="flex: 1; min-width: 120px; background: #0B0F19; padding: 0.75rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #64748B; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Step 3: Quarantine</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">Anomaly Isolation</div>
                <div style="color: #F59E0B; font-size: 0.75rem;">1,846 proxy/impossible logs quarantined</div>
            </div>
            <div style="color: #0284C7; font-size: 1.2rem;">➔</div>
            <div style="flex: 1; min-width: 120px; background: #0B0F19; padding: 0.75rem; border-radius: 6px; border: 1px solid #1E293B;">
                <div style="color: #64748B; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Step 4: Model</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">DuckDB Warehouse</div>
                <div style="color: #10B981; font-size: 0.75rem;">6 Dims, 4 Facts, 0 Orphan FKs</div>
            </div>
            <div style="color: #0284C7; font-size: 1.2rem;">➔</div>
            <div style="flex: 1; min-width: 120px; background: #0B0F19; padding: 0.75rem; border-radius: 6px; border: 1px solid #10B981;">
                <div style="color: #10B981; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Step 5: Intelligence</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">Trust Score: 94.6</div>
                <div style="color: #6EE7B7; font-size: 0.75rem;">Decision Intelligence Active</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from src.ui import inject_custom_theme, render_app_header, render_global_filter_bar
    inject_custom_theme()
    render_app_header()
    filters = render_global_filter_bar()
    render_executive_page(filters)

