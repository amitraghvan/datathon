"""Mid-Day Meal (MDM) Nutritional Welfare & Procurement Intelligence page for EduPulse AI.

Turns food commodity delivery logs into operational intelligence:
- Aggregate financial expenditure and grain volume totals
- Cost per student and unit price distributions
- Vendor performance and delivery reliability
- Peer-benchmarked IQR outlier analysis (strictly neutral, never falsely claiming fraud)
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Bootstrap workspace root for standalone execution
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_access.repository import get_procurement_summary
from src.ui.charts import chart_procurement_anomalies_scatter
from src.ui.components import (
    render_metric_card,
    render_section_header,
)
from src.ui.formatting import (
    format_inr,
    format_kg,
    format_number,
)
from src.ui.tables import render_procurement_anomaly_table


def render_procurement_page(filters: Dict[str, Any]) -> None:
    """Render the Mid-Day Meal Intelligence page."""
    df_proc = get_procurement_summary(filters)

    if df_proc.empty:
        st.warning("No procurement records match the active filter criteria.")
        return

    # 1. Top Procurement Cards
    total_spend = df_proc["total_spend_inr"].sum()
    total_qty = df_proc["total_quantity_kg"].sum()
    avg_cost_stud = df_proc["avg_cost_per_student"].mean()
    avg_cost_kg = df_proc["avg_cost_per_kg"].mean()
    schools_covered = len(df_proc)
    outliers_count = df_proc["is_procurement_outlier"].sum()

    k_cols = st.columns(5)
    with k_cols[0]:
        render_metric_card("Total MDM Spend", format_inr(total_spend, compact=True), subtitle=f"{schools_covered} schools covered", border_accent="#0284C7")
    with k_cols[1]:
        render_metric_card("Total Grain Delivered", format_kg(total_qty), subtitle=f"{format_number(total_qty / 1000, 1)} Metric Tonnes", border_accent="#10B981")
    with k_cols[2]:
        render_metric_card("Avg Spend / Pupil", format_inr(avg_cost_stud), subtitle="Annualized per enrolled pupil", border_accent="#0284C7")
    with k_cols[3]:
        render_metric_card("Weighted Cost / KG", f"₹{avg_cost_kg:.1f}", subtitle="Across 4 standard commodities", border_accent="#0284C7")
    with k_cols[4]:
        render_metric_card("Peer Exceptions", format_number(outliers_count), subtitle="Upper 1.5 IQR threshold", border_accent="#F59E0B" if outliers_count > 0 else "#10B981")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 2. Spend & Commodity Breakdown Charts
    c_dist_spend, c_grain = st.columns([1, 1])

    with c_dist_spend:
        render_section_header(
            title="Procurement Spend by District",
            subtitle="Total financial allocation across administrative districts",
            badge_text="Expenditure",
            badge_variant="neutral",
        )
        dist_spend = df_proc.groupby("district")["total_spend_inr"].sum().reset_index().sort_values(by="total_spend_inr", ascending=True)
        fig_spend = px.bar(
            dist_spend,
            x="total_spend_inr",
            y="district",
            orientation="h",
            labels={"total_spend_inr": "Total Spend (INR)", "district": "District"},
            color="total_spend_inr",
            color_continuous_scale="Blues",
        )
        fig_spend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#151D2E",
            font=dict(family="Inter, sans-serif", color="#F8FAFC"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#2A364F"),
            coloraxis_showscale=False,
            height=340,
        )
        st.plotly_chart(fig_spend, use_container_width=True)

    with c_grain:
        render_section_header(
            title="Commodity Volume Breakdown",
            subtitle="Distribution of grain types delivered under statutory price schedule",
            badge_text="Nutritional Mix",
            badge_variant="low",
        )
        grain_totals = {
            "Wheat (₹30/kg)": df_proc["wheat_kg"].sum(),
            "Rice (₹40/kg)": df_proc["rice_kg"].sum(),
            "Pulses (₹90/kg)": df_proc["pulses_kg"].sum(),
            "Cooking Oil (₹120/kg)": df_proc["oil_kg"].sum(),
        }
        df_grains = pd.DataFrame(list(grain_totals.items()), columns=["Commodity", "Volume_KG"])
        fig_grain = px.pie(
            df_grains,
            names="Commodity",
            values="Volume_KG",
            hole=0.45,
            color_discrete_sequence=["#F59E0B", "#38BDF8", "#10B981", "#EF4444"],
        )
        fig_grain.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#F8FAFC"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            height=340,
        )
        st.plotly_chart(fig_grain, use_container_width=True)

    # 3. Peer Benchmark Exceptions & Anomaly Intelligence
    render_section_header(
        title="Peer Benchmark Outlier Intelligence",
        subtitle="Evaluating per-student spend deviations against 1.5 IQR peer thresholds",
        badge_text="Operational Exceptions",
        badge_variant="high",
    )

    st.markdown("""
    <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 0.6rem 0.9rem; border-radius: 0 4px 4px 0; margin-bottom: 1rem; font-size: 0.82rem; color: #FCD34D;">
        🛡️ <strong>Governance Notice:</strong> Outliers are benchmarked against statistical peer distributions (75th percentile + 1.5 IQR). These deviations reflect operational scale (e.g. minimum delivery batch sizes in schools with < 150 students) or seasonal commodity mix skew (higher cooking oil deliveries). They are <strong>NEVER</strong> characterized as fraud without verified audit proof.
    </div>
    """, unsafe_allow_html=True)

    fig_proc_scat = chart_procurement_anomalies_scatter(df_proc)
    st.plotly_chart(fig_proc_scat, use_container_width=True)

    # 4. Outlier Schools Table
    st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.5rem;'>📋 Detailed List of Peer Benchmark Exceptions</div>", unsafe_allow_html=True)
    render_procurement_anomaly_table(df_proc)

if __name__ == "__main__":
    from src.ui import inject_custom_theme, render_app_header, render_global_filter_bar
    inject_custom_theme()
    render_app_header()
    filters = render_global_filter_bar()
    render_procurement_page(filters)
