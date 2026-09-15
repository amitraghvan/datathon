"""Welfare & Infrastructure Intelligence page for EduPulse AI.

Provides deep analytical views into:
- Physical infrastructure readiness across schools and districts
- 5 Amenity availability distributions
- Electricity impact comparison (Competition prompt requirement)
- 2x2 Welfare Gap Matrix deep-dive
- Critical Intervention quadrant isolation
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Bootstrap workspace root for standalone execution
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.data_access.repository import (
    get_electricity_comparison,
    get_filtered_schools,
)
from src.ui.cards import render_insight_card
from src.ui.charts import (
    chart_electricity_comparison,
    chart_welfare_gap_matrix,
)
from src.ui.components import (
    render_metric_card,
    render_section_header,
)
from src.ui.formatting import format_number, format_percent


def render_welfare_page(filters: Dict[str, Any]) -> None:
    """Render the Welfare & Infrastructure Intelligence page."""
    df_schools = get_filtered_schools(filters)

    if df_schools.empty:
        st.warning("No schools match active filters.")
        return

    # 1. Top Welfare Metrics
    total = len(df_schools)
    avg_infra = df_schools["infrastructure_readiness_pct"].mean()
    crit_count = (df_schools["welfare_quadrant"] == "CRITICAL INTERVENTION").sum()
    resilient_count = (df_schools["welfare_quadrant"] == "RESILIENT").sum()
    model_count = (df_schools["welfare_quadrant"] == "MODEL").sum()
    acad_interv_count = (df_schools["welfare_quadrant"] == "ACADEMIC INTERVENTION").sum()

    k_cols = st.columns(5)
    with k_cols[0]:
        render_metric_card("Avg Infrastructure", format_percent(avg_infra), subtitle="Readiness Index (0-100%)", border_accent="#0284C7")
    with k_cols[1]:
        render_metric_card("Model Schools", format_number(model_count), subtitle="High Infra, High Acad", border_accent="#10B981")
    with k_cols[2]:
        render_metric_card("Academic Intervention", format_number(acad_interv_count), subtitle="High Infra, Low Acad", border_accent="#F59E0B")
    with k_cols[3]:
        render_metric_card("Resilient Schools", format_number(resilient_count), subtitle="Low Infra, High Acad", border_accent="#06B6D4")
    with k_cols[4]:
        render_metric_card("Critical Intervention", format_number(crit_count), subtitle="Dual Deficiency", border_accent="#EF4444")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 2. Electricity Analysis Section (Competition Prompt Requirement)
    render_section_header(
        title="Analytical Focus: Functional Electricity vs. Academic Performance",
        subtitle="Comparing FLN assessment scores across schools with and without functional power",
        badge_text="Track 4 Core Question",
        badge_variant="moderate",
    )

    df_elec = get_electricity_comparison()
    c_el_chart, c_el_insight = st.columns([3, 2])
    with c_el_chart:
        fig_elec = chart_electricity_comparison(df_elec)
        st.plotly_chart(fig_elec, use_container_width=True)

    with c_el_insight:
        score_true = df_elec[df_elec["electricity_status"] == "TRUE"]["avg_academic_score"].iloc[0] if (df_elec["electricity_status"] == "TRUE").any() else 0.0
        score_false = df_elec[df_elec["electricity_status"] == "FALSE"]["avg_academic_score"].iloc[0] if (df_elec["electricity_status"] == "FALSE").any() else 0.0
        diff = score_true - score_false

        render_insight_card(
            title="Electricity Association Finding",
            finding=f"Schools with verified functional electricity average {score_true:.1f}% on FLN tests vs. {score_false:.1f}% for unpowered schools (observed delta: +{diff:.1f} pp).",
            evidence=f"Cohort of {df_elec['school_count'].sum()} schools evaluated across 100% verified inspection logs.",
            interpretation="Physical power enables extended instructional hours, digital teaching tools, and safer learning environments. However, electricity is an enabling infrastructure baseline, not an independent teacher substitute.",
            limitation="This comparison describes observed cross-sectional differences; it does NOT demonstrate direct causation. Electrification often correlates with broader community economic development.",
        )

    # 3. Amenity Availability Breakdown
    render_section_header(
        title="Statewide Amenity Availability Audit",
        subtitle="Proportion of schools with confirmed operational amenities across the cohort",
        badge_text="5 Amenities",
        badge_variant="neutral",
    )

    amenity_stats = []
    amenity_fields = [
        ("Drinking Water", "water_status"),
        ("Functional Toilet", "toilet_status"),
        ("Electricity", "electricity_status"),
        ("Boundary Wall", "boundary_status"),
        ("Playground", "playground_status"),
    ]
    for label, col in amenity_fields:
        t_cnt = (df_schools[col] == "TRUE").sum()
        f_cnt = (df_schools[col] == "FALSE").sum()
        u_cnt = (df_schools[col] == "UNKNOWN").sum()
        amenity_stats.append({
            "Amenity": label,
            "Operational (TRUE)": t_cnt,
            "Operational %": round((t_cnt / total) * 100, 1),
            "Constrained (FALSE)": f_cnt,
            "Constrained %": round((f_cnt / total) * 100, 1),
            "Uninspected (UNKNOWN)": u_cnt,
            "Uninspected %": round((u_cnt / total) * 100, 1),
        })

    df_am_display = pd.DataFrame(amenity_stats)
    st.dataframe(
        df_am_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Operational %": st.column_config.NumberColumn(format="%.1f%%"),
            "Constrained %": st.column_config.NumberColumn(format="%.1f%%"),
            "Uninspected %": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    # 4. Welfare Gap Matrix Deep Dive
    render_section_header(
        title="Welfare Gap Matrix Quadrant Distribution",
        subtitle="Exploring the 2x2 intersection between physical facilities and educational outcomes",
        badge_text="Welfare Matrix",
        badge_variant="low",
    )

    c_mat, c_list = st.columns([1, 1])
    with c_mat:
        fig_wg = chart_welfare_gap_matrix(df_schools)
        st.plotly_chart(fig_wg, use_container_width=True)

    with c_list:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.5rem;'>🚨 Critical Intervention Quadrant Review</div>", unsafe_allow_html=True)
        st.caption("Schools below both 50% Infrastructure Readiness AND 65% FLN Academic Score:")
        df_crit = df_schools[df_schools["welfare_quadrant"] == "CRITICAL INTERVENTION"][
            ["school_id", "school_name", "district", "infrastructure_readiness_pct", "academic_score", "intervention_priority_score"]
        ].sort_values(by="intervention_priority_score", ascending=False)

        st.dataframe(
            df_crit.rename(columns={
                "school_id": "ID",
                "school_name": "School Name",
                "district": "District",
                "infrastructure_readiness_pct": "Infra %",
                "academic_score": "Acad %",
                "intervention_priority_score": "Priority",
            }),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Infra %": st.column_config.NumberColumn(format="%.1f%%"),
                "Acad %": st.column_config.NumberColumn(format="%.1f%%"),
                "Priority": st.column_config.NumberColumn(format="%.1f"),
            },
        )

if __name__ == "__main__":
    from src.ui import inject_custom_theme, render_app_header, render_global_filter_bar
    inject_custom_theme()
    render_app_header()
    filters = render_global_filter_bar()
    render_welfare_page(filters)
