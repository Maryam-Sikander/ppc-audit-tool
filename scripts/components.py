import streamlit as st
import pandas as pd
import numpy as np
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

SEARCH_TERM_FORMAT = {
    "Impressions": "{:,.0f}", "Clicks": "{:,.0f}", "Orders": "{:,.0f}",
    "Spend": "${:,.2f}", "Sales": "${:,.2f}",
    "CPC": "${:.2f}", "CTR": "{:.2%}", "CVR": "{:.2%}",
    "ACOS": "{:.2%}", "ROAS": "{:.2f}",
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


def _pin_grand_total(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Separate Grand Total from data rows so it always appears at bottom.
    Returns (data_rows, grand_total_row) as a single df with Grand Total last."""
    if df.empty or group_col not in df.columns:
        return df
    is_gt = df[group_col].astype(str).str.strip() == "Grand Total"
    data_rows = df[~is_gt].copy()
    gt_rows = df[is_gt].copy()
    return pd.concat([data_rows, gt_rows], ignore_index=True)


def render_pivot(df: pd.DataFrame, group_col: str, title: str) -> pd.DataFrame:
    """Display a pivot table with formatting and pinned Grand Total row."""
    piv = pivot(df, group_col, add_grand_total=True)
    piv = _pin_grand_total(piv, group_col)
    cols = [group_col] + [c for c in PIVOT_DISPLAY_COLS if c in piv.columns]
    piv = piv[cols]
    st.markdown(f"#### {title}")

    # Highlight Grand Total row
    def _highlight_grand_total(row):
        if str(row.get(group_col, "")).strip() == "Grand Total":
            return ["font-weight: 700; background-color: #f1f5f9;"] * len(row)
        return [""] * len(row)

    styled = piv.style.format(
        {k: v for k, v in PIVOT_FORMAT.items() if k in piv.columns}
    ).apply(_highlight_grand_total, axis=1)

    st.dataframe(
        styled,
        use_container_width=True, hide_index=True,
        height=min(len(piv) * 38 + 50, 500),
    )
    return piv


def render_targeting_breakdown(df: pd.DataFrame, ad_type_label: str):
    """Render targeting breakdown for auto campaigns (Close, Loose, Substitutes, Complements)."""
    if "Targeting" not in df.columns:
        return
    
    # Filter to Auto match type rows that have targeting info
    auto_df = df[df["Match Type"] == "Auto"].copy()
    if auto_df.empty:
        return
    
    # Clean targeting values
    auto_df["Targeting"] = auto_df["Targeting"].astype(str).str.strip()
    auto_df = auto_df[~auto_df["Targeting"].isin(["", "nan", "-"])]
    if auto_df.empty:
        return

    st.markdown(f"#### {ad_type_label} — Auto Campaign Targeting Breakdown")
    piv = pivot(auto_df, "Targeting", add_grand_total=True)
    piv = _pin_grand_total(piv, "Targeting")
    cols = ["Targeting"] + [c for c in PIVOT_DISPLAY_COLS if c in piv.columns]
    piv = piv[cols]

    def _highlight_grand_total(row):
        if str(row.get("Targeting", "")).strip() == "Grand Total":
            return ["font-weight: 700; background-color: #f1f5f9;"] * len(row)
        return [""] * len(row)

    styled = piv.style.format(
        {k: v for k, v in PIVOT_FORMAT.items() if k in piv.columns}
    ).apply(_highlight_grand_total, axis=1)

    st.dataframe(
        styled,
        use_container_width=True, hide_index=True,
        height=min(len(piv) * 38 + 50, 400),
    )

    # Charts for targeting
    render_charts(piv, "Targeting", f"{ad_type_label} Auto Targeting")


def render_search_terms_tab(df: pd.DataFrame):
    """Render the Search Terms analysis sub-tab for Sponsored Products."""
    if df.empty or "Search Term" not in df.columns:
        st.info("No search term data available. Make sure the SP Search Term Report is uploaded.")
        return

    st_df = df.copy()
    st_df["Search Term"] = st_df["Search Term"].astype(str).str.strip()
    st_df = st_df[~st_df["Search Term"].isin(["", "nan", "-", "*"])]

    if st_df.empty:
        st.info("No valid search terms found in the data.")
        return

    # Aggregate by search term
    sum_cols = ["Impressions", "Clicks", "Spend", "Sales", "Orders"]
    agg = st_df.groupby("Search Term")[sum_cols].sum().reset_index()
    agg["CPC"] = np.where(agg["Clicks"] > 0, agg["Spend"] / agg["Clicks"], 0.0)
    agg["CTR"] = np.where(agg["Impressions"] > 0, agg["Clicks"] / agg["Impressions"], 0.0)
    agg["CVR"] = np.where(agg["Clicks"] > 0, agg["Orders"] / agg["Clicks"], 0.0)
    agg["ACOS"] = np.where(agg["Sales"] > 0, agg["Spend"] / agg["Sales"], 0.0)
    agg["ROAS"] = np.where(agg["Spend"] > 0, agg["Sales"] / agg["Spend"], 0.0)

    st.markdown("#### Search Terms Analysis")
    st.markdown(
        '<p style="opacity:0.6; font-size:0.9rem; margin-bottom:1rem;">'
        "Filter and analyze search terms by performance metrics.</p>",
        unsafe_allow_html=True,
    )

    # Quick filters
    st.markdown("##### Quick Filters")
    filter_options = [
        "All Search Terms",
        "ACOS Under 30%",
        "ACOS 30% - 50%",
        "ACOS Over 50%",
        "10+ Clicks, No Sales",
        "5+ Clicks, No Sales",
        "High CVR (>15%)",
        "Top Revenue Generators",
        "Top Order Generators",
    ]
    selected_filter = st.selectbox("Select a filter", filter_options, key="st_filter")

    if selected_filter == "ACOS Under 30%":
        filtered = agg[(agg["ACOS"] > 0) & (agg["ACOS"] < 0.30)]
    elif selected_filter == "ACOS 30% - 50%":
        filtered = agg[(agg["ACOS"] >= 0.30) & (agg["ACOS"] <= 0.50)]
    elif selected_filter == "ACOS Over 50%":
        filtered = agg[agg["ACOS"] > 0.50]
    elif selected_filter == "10+ Clicks, No Sales":
        filtered = agg[(agg["Clicks"] >= 10) & (agg["Orders"] == 0)]
    elif selected_filter == "5+ Clicks, No Sales":
        filtered = agg[(agg["Clicks"] >= 5) & (agg["Orders"] == 0)]
    elif selected_filter == "High CVR (>15%)":
        filtered = agg[agg["CVR"] > 0.15]
    elif selected_filter == "Top Revenue Generators":
        filtered = agg[agg["Sales"] > 0].nlargest(50, "Sales")
    elif selected_filter == "Top Order Generators":
        filtered = agg[agg["Orders"] > 0].nlargest(50, "Orders")
    else:
        filtered = agg

    if filtered.empty:
        st.warning("No search terms match the selected filter.")
        return

    # Sort options
    sort_col = st.selectbox(
        "Sort by",
        ["Spend", "Sales", "Clicks", "Orders", "ACOS", "CVR", "ROAS", "CPC", "Impressions"],
        key="st_sort",
    )
    sort_asc = st.checkbox("Sort ascending", value=False, key="st_asc")
    filtered = filtered.sort_values(sort_col, ascending=sort_asc)

    # Summary metrics for filtered terms
    cols = st.columns(5)
    filter_summary = [
        ("Terms", f"{len(filtered):,}", "#475569"),
        ("Total Spend", f"${filtered['Spend'].sum():,.2f}", "#dc2626"),
        ("Total Sales", f"${filtered['Sales'].sum():,.2f}", "#059669"),
        ("Total Orders", f"{int(filtered['Orders'].sum()):,}", "#2563eb"),
        ("Avg ACOS", f"{(filtered['Spend'].sum() / filtered['Sales'].sum()):.2%}" if filtered['Sales'].sum() > 0 else "N/A", "#d97706"),
    ]
    for col, (lbl, val, clr) in zip(cols, filter_summary):
        col.markdown(kpi_tile(lbl, val, clr), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display data
    display_cols = ["Search Term", "Impressions", "Clicks", "Spend", "Sales", "Orders",
                    "CPC", "CTR", "CVR", "ACOS", "ROAS"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].style.format(
            {k: v for k, v in SEARCH_TERM_FORMAT.items() if k in filtered.columns}
        ),
        use_container_width=True,
        hide_index=True,
        height=min(len(filtered) * 38 + 50, 600),
    )

    # Top/Bottom performers charts
    st.markdown("---")
    if len(filtered[filtered["Sales"] > 0]) >= 2:
        col_a, col_b = st.columns(2)
        with col_a:
            top_revenue = filtered[filtered["Sales"] > 0].nlargest(10, "Sales")
            fig = go.Figure(go.Bar(
                y=top_revenue["Search Term"], x=top_revenue["Sales"],
                orientation="h", marker_color=Theme.COLORS["success"],
                text=top_revenue["Sales"].apply(lambda x: f"${x:,.0f}"),
                textposition="outside",
            ))
            fig.update_layout(
                title="Top 10 Search Terms by Sales",
                height=400, yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color=Theme.COLORS["text"],
                margin=dict(l=200, r=60, t=50, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            top_spend = filtered[filtered["Orders"] == 0].nlargest(10, "Spend") if len(filtered[filtered["Orders"] == 0]) > 0 else filtered.nlargest(10, "Spend")
            fig = go.Figure(go.Bar(
                y=top_spend["Search Term"], x=top_spend["Spend"],
                orientation="h", marker_color=Theme.COLORS["danger"],
                text=top_spend["Spend"].apply(lambda x: f"${x:,.0f}"),
                textposition="outside",
            ))
            fig.update_layout(
                title="Top Wasted Spend (No Orders)" if len(filtered[filtered["Orders"] == 0]) > 0 else "Top 10 by Spend",
                height=400, yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color=Theme.COLORS["text"],
                margin=dict(l=200, r=60, t=50, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)


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
