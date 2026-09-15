"""Global cascading filter component for EduPulse AI."""

from typing import Any, Dict

import streamlit as st

from src.data_access.repository import get_all_schools_enriched, get_dim_filters


def render_global_filter_bar() -> Dict[str, Any]:
    """Render the responsive global filter strip with cascading updates."""
    dim_data = get_dim_filters()
    df_all = get_all_schools_enriched()

    # Initialize filter state if not present
    if "filters" not in st.session_state:
        st.session_state["filters"] = {
            "district": "All",
            "block": "All",
            "school_type": "All",
            "medium": "All",
            "risk_level": "All",
            "primary_driver": "All",
            "welfare_quadrant": "All",
        }

    current_filters = st.session_state["filters"]

    with st.expander("⚙️ **Global Scope & Demographic Filters** (Cascading)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)

        # 1. District Filter
        with c1:
            district_opts = ["All"] + dim_data["districts"]
            dist_idx = district_opts.index(current_filters["district"]) if current_filters["district"] in district_opts else 0
            sel_dist = st.selectbox("District", district_opts, index=dist_idx, key="filter_dist")
            if sel_dist != current_filters["district"]:
                current_filters["district"] = sel_dist
                current_filters["block"] = "All"  # Reset child block on district change

        # 2. Block Filter (Cascaded from District)
        with c2:
            if current_filters["district"] != "All":
                avail_blocks = sorted(df_all[df_all["district"] == current_filters["district"]]["block"].dropna().unique().tolist())
            else:
                avail_blocks = dim_data["blocks"]
            block_opts = ["All"] + avail_blocks
            block_idx = block_opts.index(current_filters["block"]) if current_filters["block"] in block_opts else 0
            sel_block = st.selectbox("Block", block_opts, index=block_idx, key="filter_block")
            current_filters["block"] = sel_block

        # 3. School Type
        with c3:
            stype_opts = ["All"] + dim_data["school_types"]
            stype_idx = stype_opts.index(current_filters["school_type"]) if current_filters["school_type"] in stype_opts else 0
            sel_stype = st.selectbox("School Level", stype_opts, index=stype_idx, key="filter_stype")
            current_filters["school_type"] = sel_stype

        # 4. Medium of Instruction
        with c4:
            med_opts = ["All"] + dim_data["mediums"]
            med_idx = med_opts.index(current_filters["medium"]) if current_filters["medium"] in med_opts else 0
            sel_med = st.selectbox("Medium", med_opts, index=med_idx, key="filter_med")
            current_filters["medium"] = sel_med

        c5, c6, c7, c8 = st.columns(4)

        # 5. Risk Band
        with c5:
            risk_opts = ["All"] + dim_data["risk_levels"]
            risk_idx = risk_opts.index(current_filters["risk_level"]) if current_filters["risk_level"] in risk_opts else 0
            sel_risk = st.selectbox("Risk Severity Tier", risk_opts, index=risk_idx, key="filter_risk")
            current_filters["risk_level"] = sel_risk

        # 6. Primary Driver
        with c6:
            driver_opts = ["All"] + dim_data["drivers"]
            driver_idx = driver_opts.index(current_filters["primary_driver"]) if current_filters["primary_driver"] in driver_opts else 0
            sel_driver = st.selectbox("Primary Vulnerability Driver", driver_opts, index=driver_idx, key="filter_driver")
            current_filters["primary_driver"] = sel_driver

        # 7. Welfare Quadrant
        with c7:
            quad_opts = ["All"] + dim_data["welfare_quadrants"]
            quad_idx = quad_opts.index(current_filters["welfare_quadrant"]) if current_filters["welfare_quadrant"] in quad_opts else 0
            sel_quad = st.selectbox("Welfare Matrix Quadrant", quad_opts, index=quad_idx, key="filter_quad")
            current_filters["welfare_quadrant"] = sel_quad

        # 8. Reset Action
        with c8:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("↺ Reset All Filters", use_container_width=True):
                st.session_state["filters"] = {
                    "district": "All",
                    "block": "All",
                    "school_type": "All",
                    "medium": "All",
                    "risk_level": "All",
                    "primary_driver": "All",
                    "welfare_quadrant": "All",
                }
                st.rerun()

    # Active Filter Chips Indicator
    active_filters = {k: v for k, v in current_filters.items() if v != "All"}
    if active_filters:
        chips = " &nbsp;|&nbsp; ".join([f"<strong>{k.replace('_', ' ').title()}:</strong> {v}" for k, v in active_filters.items()])
        st.markdown(
            f"<div style='background: #151D2E; border: 1px solid #2A364F; padding: 0.35rem 0.8rem; border-radius: 4px; font-size: 0.78rem; color: #94A3B8; margin-bottom: 1rem;'>"
            f"🔍 Active Scope: {chips}</div>",
            unsafe_allow_html=True,
        )

    return current_filters
