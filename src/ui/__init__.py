"""UI presentation layer for EduPulse AI."""

from .alerts import render_dynamic_alert_strip
from .cards import (
    render_amenity_status_cards,
    render_insight_card,
    render_intervention_decision_panel,
    render_school_profile_header,
)
from .charts import (
    chart_attendance_academic_association,
    chart_district_performance,
    chart_electricity_comparison,
    chart_procurement_anomalies_scatter,
    chart_risk_vs_priority_scatter,
    chart_school_attendance_timeseries,
    chart_welfare_gap_matrix,
)
from .components import (
    render_badge,
    render_data_lineage_card,
    render_empty_state,
    render_metric_card,
    render_section_header,
)
from .filters import render_global_filter_bar
from .formatting import (
    format_gap,
    format_inr,
    format_kg,
    format_number,
    format_percent,
)
from .layout import render_app_header
from .tables import (
    render_data_quality_audit_table,
    render_priority_schools_table,
    render_procurement_anomaly_table,
)
from .theme import inject_custom_theme

__all__ = [
    "inject_custom_theme",
    "render_app_header",
    "render_global_filter_bar",
    "render_dynamic_alert_strip",
    "render_metric_card",
    "render_section_header",
    "render_badge",
    "render_empty_state",
    "render_data_lineage_card",
    "render_school_profile_header",
    "render_amenity_status_cards",
    "render_intervention_decision_panel",
    "render_insight_card",
    "chart_district_performance",
    "chart_risk_vs_priority_scatter",
    "chart_welfare_gap_matrix",
    "chart_attendance_academic_association",
    "chart_school_attendance_timeseries",
    "chart_electricity_comparison",
    "chart_procurement_anomalies_scatter",
    "render_priority_schools_table",
    "render_procurement_anomaly_table",
    "render_data_quality_audit_table",
    "format_number",
    "format_percent",
    "format_inr",
    "format_kg",
    "format_gap",
]
