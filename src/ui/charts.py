"""Plotly chart definitions for EduPulse AI.

Adheres to executive visual standards:
- Dark slate backgrounds matching the UI theme
- High contrast, semantic color assignments
- Informative tooltips with context
- Explicit non-causal captions
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "#151D2E",
    "font": {"family": "Inter, -apple-system, sans-serif", "color": "#F8FAFC", "size": 12},
    "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    "hoverlabel": {
        "bgcolor": "#0B0F19",
        "bordercolor": "#2A364F",
        "font": {"family": "Inter, sans-serif", "size": 12, "color": "#F8FAFC"},
    },
}

def chart_district_performance(
    df_dist: pd.DataFrame,
    metric_col: str = "avg_attendance_rate",
    metric_label: str = "Average Attendance Rate (%)",
) -> go.Figure:
    """Render horizontal ranked bar chart of district performance."""
    df_sorted = df_dist.sort_values(by=metric_col, ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted["district"],
        x=df_sorted[metric_col],
        orientation="h",
        marker=dict(
            color=df_sorted[metric_col],
            colorscale=[[0.0, "#0284C7"], [1.0, "#38BDF8"]],
            line=dict(color="#2A364F", width=1),
        ),
        hovertemplate=(
            "<b>%{y} District</b><br>"
            + f"{metric_label}: " + "%{x:.1f}%<br>"
            + "Schools: %{customdata[0]}<br>"
            + "Total Enrolled: %{customdata[1]:,}<extra></extra>"
        ),
        customdata=df_sorted[["school_count", "total_enrolled_students"]].values,
    ))

    # Add peer state average vertical line
    mean_val = df_dist[metric_col].mean()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text=f"Cohort Mean: {mean_val:.1f}%",
        annotation_position="top right",
        annotation_font=dict(color="#FCD34D", size=10),
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=f"<b>{metric_label} by District</b>", font=dict(size=14, color="#F8FAFC")),
        xaxis=dict(title=metric_label, gridcolor="#2A364F", zeroline=False),
        yaxis=dict(title=None, gridcolor="rgba(0,0,0,0)"),
        height=360,
    )
    return fig

def chart_risk_vs_priority_scatter(df_schools: pd.DataFrame) -> go.Figure:
    """Render scatter plot demonstrating the vital distinction between Risk Severity and Intervention Priority."""
    fig = px.scatter(
        df_schools,
        x="risk_score",
        y="intervention_priority_score",
        color="primary_risk_driver",
        size="enrollment",
        hover_name="school_name",
        hover_data={
            "school_id": True,
            "district": True,
            "risk_score": ":.1f",
            "intervention_priority_score": ":.1f",
            "enrollment": ":,",
            "primary_risk_driver": True,
        },
        color_discrete_map={
            "INFRASTRUCTURE": "#F59E0B",
            "ACADEMIC": "#0284C7",
            "ATTENDANCE": "#8B5CF6",
            "MULTI_FACTOR": "#EF4444",
        },
        labels={
            "risk_score": "Observed Vulnerability Severity (Risk Score 0-100)",
            "intervention_priority_score": "Intervention Urgency (Priority Score 0-100)",
            "primary_risk_driver": "Primary Driver",
        },
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="<b>Risk Severity vs. Intervention Priority</b><br><span style='font-size:10px; color:#94A3B8;'>Severity evaluates vulnerability; Priority evaluates who should be reviewed first</span>",
            font=dict(size=13),
        ),
        xaxis=dict(gridcolor="#2A364F", range=[0, 100]),
        yaxis=dict(gridcolor="#2A364F", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
    )
    return fig

def chart_welfare_gap_matrix(df_schools: pd.DataFrame) -> go.Figure:
    """Render 2x2 Welfare Gap Matrix (Infrastructure Readiness vs Academic FLN Score)."""
    fig = px.scatter(
        df_schools,
        x="infrastructure_readiness_pct",
        y="academic_score",
        color="welfare_quadrant",
        hover_name="school_name",
        hover_data={
            "school_id": True,
            "district": True,
            "infrastructure_readiness_pct": ":.1f%",
            "academic_score": ":.1f%",
            "attendance_rate": ":.1f%",
            "intervention_priority_score": ":.1f",
        },
        color_discrete_map={
            "MODEL": "#10B981",
            "ACADEMIC INTERVENTION": "#F59E0B",
            "RESILIENT": "#06B6D4",
            "CRITICAL INTERVENTION": "#EF4444",
        },
        labels={
            "infrastructure_readiness_pct": "Infrastructure Readiness Index (%)",
            "academic_score": "Normalized FLN Academic Score (%)",
            "welfare_quadrant": "Quadrant",
        },
    )

    # Add quadrant threshold dividing lines
    fig.add_vline(x=50.0, line_dash="dash", line_color="#64748B", line_width=1.5)
    fig.add_hline(y=65.0, line_dash="dash", line_color="#64748B", line_width=1.5)

    # Quadrant annotations
    annotations = [
        dict(x=75, y=85, text="<b>MODEL</b><br>High Infra, High Academics", showarrow=False, font=dict(color="#10B981", size=11)),
        dict(x=25, y=85, text="<b>RESILIENT</b><br>Low Infra, High Academics", showarrow=False, font=dict(color="#06B6D4", size=11)),
        dict(x=75, y=45, text="<b>ACADEMIC INTERVENTION</b><br>High Infra, Low Academics", showarrow=False, font=dict(color="#FCD34D", size=11)),
        dict(x=25, y=45, text="<b>CRITICAL INTERVENTION</b><br>Low Infra, Low Academics", showarrow=False, font=dict(color="#FCA5A5", size=11)),
    ]
    for ann in annotations:
        fig.add_annotation(**ann)

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="<b>School Welfare Gap Matrix (2x2 Architecture)</b>", font=dict(size=14)),
        xaxis=dict(gridcolor="#2A364F", range=[0, 100]),
        yaxis=dict(gridcolor="#2A364F", range=[20, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
    )
    return fig

def chart_attendance_academic_association(
    df_schools: pd.DataFrame,
    pearson_r: float = 0.453,
    spearman_rho: float = 0.448,
    sample_size: int = 600,
) -> go.Figure:
    """Render scatter plot of attendance vs academic performance with non-causal trendline."""
    fig = px.scatter(
        df_schools,
        x="attendance_rate",
        y="academic_score",
        color="district",
        trendline="ols",
        trendline_color_override="#38BDF8",
        hover_name="school_name",
        hover_data={
            "school_id": True,
            "district": True,
            "attendance_rate": ":.1f%",
            "academic_score": ":.1f%",
        },
        labels={
            "attendance_rate": "Student Attendance Rate (%)",
            "academic_score": "FLN Academic Score (%)",
            "district": "District",
        },
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>Student Attendance vs. FLN Academic Scores</b><br><span style='font-size:11px; color:#94A3B8;'>Pearson r = {pearson_r:.3f} (p < 0.001) | Spearman rho = {spearman_rho:.3f} | N = {sample_size} schools (Association, not causation)</span>",
            font=dict(size=13),
        ),
        xaxis=dict(gridcolor="#2A364F", range=[40, 100]),
        yaxis=dict(gridcolor="#2A364F", range=[30, 100]),
        height=420,
    )
    return fig

def chart_school_attendance_timeseries(df_att: pd.DataFrame) -> go.Figure:
    """Render daily attendance tracking history with anomaly markers for School 360."""
    fig = go.Figure()

    # Trusted records line
    df_trusted = df_att[df_att["is_trusted_attendance"]].sort_values(by="date")
    fig.add_trace(go.Scatter(
        x=df_trusted["date"],
        y=df_trusted["attendance_rate"],
        mode="lines+markers",
        name="Trusted Daily Attendance",
        line=dict(color="#0284C7", width=2),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Attendance: %{y:.1f}%<br>Students: %{customdata[0]} / %{customdata[1]}<extra></extra>",
        customdata=df_trusted[["present_students", "total_students"]].values,
    ))

    # Flagged proxy records
    df_proxy = df_att[df_att["is_proxy_attendance"]]
    if not df_proxy.empty:
        fig.add_trace(go.Scatter(
            x=df_proxy["date"],
            y=df_proxy["attendance_rate"],
            mode="markers",
            name="Sunday Proxy Flag (Quarantined)",
            marker=dict(color="#F59E0B", size=8, symbol="triangle-up"),
            hovertemplate="<b>%{x} (Sunday Proxy)</b><br>Attendance: %{y:.1f}%<extra></extra>",
        ))

    # Flagged impossible records
    df_imp = df_att[df_att["is_impossible_attendance"]]
    if not df_imp.empty:
        fig.add_trace(go.Scatter(
            x=df_imp["date"],
            y=df_imp["attendance_rate"],
            mode="markers",
            name="Impossible Record (Quarantined)",
            marker=dict(color="#EF4444", size=9, symbol="x"),
            hovertemplate="<b>%{x} (Impossible)</b><br>Attendance: %{y:.1f}%<extra></extra>",
        ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="<b>Daily Attendance Trend & Data Trust Quarantine</b>", font=dict(size=13)),
        xaxis=dict(title="Observation Date", gridcolor="#2A364F"),
        yaxis=dict(title="Attendance Rate (%)", gridcolor="#2A364F", range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320,
    )
    return fig

def chart_electricity_comparison(df_elec: pd.DataFrame) -> go.Figure:
    """Render comparison of test scores by electricity availability status."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_elec["electricity_status"],
        y=df_elec["avg_academic_score"],
        marker=dict(
            color=["#10B981" if s == "TRUE" else ("#EF4444" if s == "FALSE" else "#F59E0B") for s in df_elec["electricity_status"]],
        ),
        text=df_elec["avg_academic_score"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate=(
            "<b>Electricity Status: %{x}</b><br>"
            + "Avg FLN Score: %{y:.1f}%<br>"
            + "Schools: %{customdata[0]}<br>"
            + "Enrolled Students: %{customdata[1]:,}<extra></extra>"
        ),
        customdata=df_elec[["school_count", "total_enrolled"]].values,
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="<b>Academic Learning Outcomes by School Electricity Availability</b><br><span style='font-size:10px; color:#94A3B8;'>Observed cross-sectional comparison; does not demonstrate direct causation.</span>",
            font=dict(size=13),
        ),
        xaxis=dict(title="Electricity Functional Status", gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Average Academic Score (%)", gridcolor="#2A364F", range=[0, 85]),
        height=320,
    )
    return fig

def chart_procurement_anomalies_scatter(df_proc: pd.DataFrame) -> go.Figure:
    """Render procurement spend per student vs enrollment, highlighting peer IQR exceptions."""
    fig = px.scatter(
        df_proc,
        x="enrollment",
        y="avg_cost_per_student",
        color="is_procurement_outlier",
        hover_name="school_name",
        hover_data={
            "school_id": True,
            "district": True,
            "enrollment": ":,",
            "avg_cost_per_student": "₹:.1f",
            "total_spend_inr": "₹:,.0f",
            "procurement_anomaly_reason": True,
        },
        color_discrete_map={
            False: "#0284C7",
            True: "#F59E0B",
        },
        labels={
            "enrollment": "Total Enrolled Students",
            "avg_cost_per_student": "Procurement Cost Per Student (₹)",
            "is_procurement_outlier": "Peer Benchmark Exception",
        },
    )

    # 1.5 IQR peer cutoff horizontal line
    q3 = df_proc["avg_cost_per_student"].quantile(0.75)
    iqr = q3 - df_proc["avg_cost_per_student"].quantile(0.25)
    cutoff = q3 + 1.5 * iqr

    fig.add_hline(
        y=cutoff,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text=f"Peer 75th + 1.5 IQR Cutoff: ₹{cutoff:.1f}",
        annotation_position="top right",
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(
            text="<b>Procurement Cost Per Student vs. Enrollment Scale</b><br><span style='font-size:10px; color:#94A3B8;'>Exceptions reflect small enrollment delivery batches or commodity mix skew, not verified fraud</span>",
            font=dict(size=13),
        ),
        xaxis=dict(title="Total Enrolled Students", gridcolor="#2A364F"),
        yaxis=dict(title="Cost Per Student (INR)", gridcolor="#2A364F"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
    )
    return fig
