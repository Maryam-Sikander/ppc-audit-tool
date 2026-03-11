import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scripts import visualizations as viz
from calculations import pivot, add_metrics, kpi_summary
from scripts.config import Theme


PIVOT_DISPLAY_COLS = [
    "Impressions", "Clicks", "Spend", "Sales", "Units", "Waste Spend",
    "CPC", "CTR", "CVR", "ACOS", "% Adspend", "% Ad Sale", "CAC",
]

PIVOT_FORMAT = {
    "Impressions": "{:,.0f}", "Clicks": "{:,.0f}", "Units": "{:,.0f}",
    "Spend": "${:,.2f}", "Sales": "${:,.2f}", "Waste Spend": "${:,.2f}",
    "CPC": "${:.2f}", "CTR": "{:.2%}", "CVR": "{:.2%}",
    "ACOS": "{:.2%}", "% Adspend": "{:.2%}", "% Ad Sale": "{:.2%}",
    "CAC": "${:.2f}",
}

AD_TYPE_SUMMARY_FORMAT = {
    "Sales": "${:,.2f}", "Spend": "${:,.2f}", "Impressions": "{:,.0f}",
    "Clicks": "{:,.0f}", "Units": "{:,.0f}",
    "ACOS": "{:.2%}", "CTR": "{:.2%}", "CVR": "{:.2%}",
    "CPC": "${:.2f}", "ROAS": "{:.2f}",
    "% Spend Share": "{:.2%}", "% Sale Share": "{:.2%}",
}

WASTED_FORMAT = {
    "Total Spend": "${:,.2f}", "Wasted Spend": "${:,.2f}",
    "% Wasted Spend": "{:.2%}", "Clicks": "{:,.0f}",
    "Wasted Clicks": "{:,.0f}", "% Wasted Clicks": "{:.2%}",
}


def kpi_tile(label: str, value: str, accent: str = "#0f172a") -> str:
    """Return HTML for a Tableau/Power BI-style KPI tile."""
    return f"""
    <div class="kpi-tile">
        <div style="
            height: 3px;
            background: {accent};
            border-radius: 4px 4px 0 0;
        "></div>
        <div style="padding: 1rem 1.25rem; text-align: center;">
            <div style="
                font-size: 0.68rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #64748b;
                margin-bottom: 0.4rem;
            ">{label}</div>
            <div style="
                font-size: 1.55rem;
                font-weight: 700;
                color: #1e293b;
                letter-spacing: -0.01em;
            ">{value}</div>
        </div>
    </div>"""


def render_pivot(df: pd.DataFrame, group_col: str, title: str) -> pd.DataFrame:
    """Display a pivot table with formatting and Grand Total row."""
    piv = pivot(df, group_col, add_grand_total=True)
    cols = [group_col] + [c for c in PIVOT_DISPLAY_COLS if c in piv.columns]
    piv = piv[cols]
    st.markdown(f"#### {title}")
    st.dataframe(
        piv.style.format({k: v for k, v in PIVOT_FORMAT.items() if k in piv.columns}),
        use_container_width=True, hide_index=True,
        height=min(len(piv) * 38 + 50, 500),
    )
    return piv


def render_spend_sales_line(df: pd.DataFrame, date_col: str = "Date", title: str = "Spend vs Sales Over Time"):
    if date_col not in df.columns or not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        return
    daily = df.groupby(date_col)[["Spend", "Sales"]].sum().reset_index().sort_values(date_col)
    if daily.empty or len(daily) < 2:
        return
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=daily[date_col], y=daily["Spend"], name="Spend",
        fill="tozeroy", line=dict(color=Theme.COLORS["danger"], width=2),
        fillcolor="rgba(220,38,38,0.08)",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=daily[date_col], y=daily["Sales"], name="Sales",
        line=dict(color=Theme.COLORS["success"], width=2),
    ), secondary_y=True)
    fig.update_layout(
        title=title, height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color=Theme.COLORS["text"],
        xaxis=dict(showgrid=False),
        yaxis=dict(title="Spend ($)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        yaxis2=dict(title="Sales ($)"),
        margin=dict(l=60, r=40, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_charts(piv: pd.DataFrame, group_col: str, label: str):
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(viz.plot_spend_vs_sales(piv, group_col, f"{label} — Spend vs Sales"), use_container_width=True)
    with col_b:
        st.plotly_chart(viz.plot_spend_distribution(piv, group_col, "Spend", f"{label} — Spend Distribution"), use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.plotly_chart(viz.plot_acos_comparison(piv, group_col, f"{label} — ACOS Comparison"), use_container_width=True)
    with col_d:
        st.plotly_chart(viz.plot_wasted_spend_bar(piv, group_col, f"{label} — Spend Efficiency"), use_container_width=True)

    st.plotly_chart(viz.plot_efficiency_metrics(piv, group_col, f"{label} — CPC / CTR / CVR Breakdown"), use_container_width=True)
