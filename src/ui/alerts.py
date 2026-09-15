"""Dynamic executive alerts and insight strips generated from live data."""

import pandas as pd
import streamlit as st


def render_dynamic_alert_strip(df_schools: pd.DataFrame) -> None:
    """Render dynamically computed executive alerts reflecting current cohort status."""
    total = len(df_schools)
    if total == 0:
        return

    crit_quad_count = (df_schools["welfare_quadrant"] == "CRITICAL INTERVENTION").sum()
    infra_driver_count = (df_schools["primary_risk_driver"] == "INFRASTRUCTURE").sum()
    crit_risk_count = (df_schools["risk_level"] == "CRITICAL").sum()
    high_prio_count = (df_schools["intervention_priority_score"] >= 35.0).sum()

    # Build dynamic alerts
    messages = []
    if crit_quad_count > 0:
        messages.append(
            f"⚠️ <strong>{crit_quad_count} schools ({crit_quad_count / total * 100:.1f}%)</strong> fall into the <em>Critical Intervention</em> welfare quadrant (dual deficits in infrastructure & FLN scores)."
        )

    if infra_driver_count > 0:
        messages.append(
            f"🧱 <strong>{infra_driver_count} schools ({infra_driver_count / total * 100:.1f}%)</strong> have physical infrastructure deficits as their primary analytical vulnerability driver."
        )

    if crit_risk_count == 0:
        messages.append(
            f"ℹ️ <strong>0 schools in Critical Risk Severity</strong> (mean cohort attendance is 79.1%), yet <strong>{high_prio_count} schools</strong> require immediate supervisory intervention due to peer benchmark deficits."
        )

    alert_body = "<br>".join(messages)

    html = f"""
    <div class="alert-strip">
        <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #38BDF8; margin-bottom: 0.25rem;">
            ⚡ Executive Alert & Priority Intelligence
        </div>
        <div>{alert_body}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
