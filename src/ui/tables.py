"""Styled, sortable, and paginated data table components for EduPulse AI."""

from typing import Callable, Optional

import pandas as pd
import streamlit as st


def render_priority_schools_table(
    df_schools: pd.DataFrame,
    on_select_school: Optional[Callable[[str], None]] = None,
    page_size: int = 10,
) -> None:
    """Render top intervention priority schools with drilldown action."""
    # Ensure ordered by intervention rank
    df_sorted = df_schools.sort_values(
        by=["intervention_priority_score", "enrollment", "school_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    total_rows = len(df_sorted)
    if total_rows == 0:
        st.info("No schools match the current filter criteria.")
        return

    # Table Controls
    col_search, col_page = st.columns([3, 1])
    with col_search:
        search_term = st.text_input(
            "🔍 Search priority schools by name, ID, or district:",
            key="priority_table_search",
            placeholder="e.g. Sama, SCH0386, Sangrur...",
        )
    if search_term:
        mask = (
            df_sorted["school_name"].str.contains(search_term, case=False, na=False)
            | df_sorted["school_id"].str.contains(search_term, case=False, na=False)
            | df_sorted["district"].str.contains(search_term, case=False, na=False)
        )
        df_sorted = df_sorted[mask].reset_index(drop=True)
        total_rows = len(df_sorted)

    # Simple pagination
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    with col_page:
        page_num = st.number_input(
            f"Page (of {total_pages})", min_value=1, max_value=total_pages, value=1, step=1, key="priority_page"
        )

    start_idx = (page_num - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)
    df_page = df_sorted.iloc[start_idx:end_idx].copy()

    # Render formatted table using st.dataframe
    display_cols = [
        "intervention_rank",
        "school_id",
        "school_name",
        "district",
        "intervention_priority_score",
        "risk_score",
        "primary_risk_driver",
        "attendance_rate",
        "academic_score",
        "infrastructure_readiness_pct",
    ]

    rename_map = {
        "intervention_rank": "Rank",
        "school_id": "School ID",
        "school_name": "School Name",
        "district": "District",
        "intervention_priority_score": "Priority Score",
        "risk_score": "Risk Score",
        "primary_risk_driver": "Primary Driver",
        "attendance_rate": "Attendance (%)",
        "academic_score": "Academics (%)",
        "infrastructure_readiness_pct": "Infra (%)",
    }

    df_display = df_page[display_cols].rename(columns=rename_map)

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Priority Score": st.column_config.NumberColumn(format="%.1f"),
            "Risk Score": st.column_config.NumberColumn(format="%.1f"),
            "Attendance (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Academics (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Infra (%)": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    # School selection drilldown row
    st.markdown("<div style='font-size: 0.8rem; color: #94A3B8; margin-top: 0.5rem;'>💡 Select a school from the current page to open its <strong>School 360</strong> profile:</div>", unsafe_allow_html=True)
    sel_cols = st.columns(len(df_page))
    for col, (_, row) in zip(sel_cols, df_page.iterrows()):
        with col:
            sid = row["school_id"]
            if st.button(f"#{row['intervention_rank']} {sid}", key=f"drill_{sid}", use_container_width=True):
                st.session_state["selected_school_id"] = sid
                st.session_state["current_page"] = "School 360"
                st.rerun()

def render_procurement_anomaly_table(df_anom: pd.DataFrame) -> None:
    """Render table of schools with procurement peer benchmark exceptions."""
    df_outliers = df_anom[df_anom["is_procurement_outlier"]].sort_values(by="avg_cost_per_student", ascending=False)

    if df_outliers.empty:
        st.info("No procurement peer benchmark exceptions found for active filters.")
        return

    display_df = df_outliers[[
        "school_id",
        "school_name",
        "district",
        "enrollment",
        "avg_cost_per_student",
        "avg_cost_per_kg",
        "total_spend_inr",
        "procurement_anomaly_reason",
    ]].rename(columns={
        "school_id": "School ID",
        "school_name": "School Name",
        "district": "District",
        "enrollment": "Enrollment",
        "avg_cost_per_student": "Cost/Student (₹)",
        "avg_cost_per_kg": "Cost/KG (₹)",
        "total_spend_inr": "Total Spend (₹)",
        "procurement_anomaly_reason": "Operational Exception Context",
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost/Student (₹)": st.column_config.NumberColumn(format="₹%.1f"),
            "Cost/KG (₹)": st.column_config.NumberColumn(format="₹%.1f"),
            "Total Spend (₹)": st.column_config.NumberColumn(format="₹%,.0f"),
            "Enrollment": st.column_config.NumberColumn(format="%d"),
        },
    )

def render_data_quality_audit_table() -> None:
    """Render the 10 data engineering quality gates and rescue reconciliation."""
    quality_gates = [
        {"Gate": "1. Raw Immutability", "Dataset": "All Sources", "Flagged": "0 bytes", "Action": "Strict read-only ingestion; no raw files touched", "Status": "PASS"},
        {"Gate": "2. School ID Entity Resolution", "Dataset": "School Master", "Flagged": "18 duplicates", "Action": "Canonical SCHxxxx mapping with 100% key match", "Status": "PASS"},
        {"Gate": "3. Date Normalization", "Dataset": "Attendance/Infra/MDM", "Flagged": "2,190 strings", "Action": "Harmonized 6 patterns across 365 calendar days", "Status": "PASS"},
        {"Gate": "4. Multilingual Booleans", "Dataset": "Infrastructure", "Flagged": "Unknown tokens", "Action": "Standardized to TRUE/FALSE/UNKNOWN (UNKNOWN != FALSE)", "Status": "PASS"},
        {"Gate": "5. Impossible Attendance", "Dataset": "Attendance", "Flagged": "835 records", "Action": "Quarantined present > total without mutating raw logs", "Status": "PASS"},
        {"Gate": "6. Sunday Proxy Fraud", "Dataset": "Attendance", "Flagged": "1,011 records", "Action": "Quarantined 100% Sunday logs from trusted metrics", "Status": "PASS"},
        {"Gate": "7. Unit Rescue & Constants", "Dataset": "Procurement", "Flagged": "2,555 missing", "Action": "Rescued via verified prices (Wheat ₹30, Rice ₹40, Pulses ₹90, Oil ₹120)", "Status": "PASS"},
        {"Gate": "8. Assessment Normalization", "Dataset": "FLN Tests", "Flagged": "6 grading scales", "Action": "Standardized to 0-100%; tracked letter proxy sensitivity", "Status": "PASS"},
        {"Gate": "9. District Hierarchy", "Dataset": "School Master", "Flagged": "21 missing", "Action": "Imputed deterministically via 1:1 Punjab block hierarchy", "Status": "PASS"},
        {"Gate": "10. Star Schema Integrity", "Dataset": "DuckDB Warehouse", "Flagged": "0 orphans", "Action": "Validated foreign key relationships across 4 fact tables", "Status": "PASS"},
    ]

    df_qg = pd.DataFrame(quality_gates)
    st.dataframe(df_qg, use_container_width=True, hide_index=True)
