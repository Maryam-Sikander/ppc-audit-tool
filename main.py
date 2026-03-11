import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from calculations import normalize_report, add_metrics, kpi_summary, pivot, export_excel
from scripts.components import kpi_tile, render_pivot, render_spend_sales_line, render_charts
from scripts.components import AD_TYPE_SUMMARY_FORMAT, WASTED_FORMAT
from scripts.config import Theme

st.set_page_config(
    page_title="PPC Audit Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with open("s.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass


@st.cache_data(show_spinner=False)
def read_file(uploaded):
    if uploaded is None:
        return None
    try:
        if uploaded.name.lower().endswith(".csv"):
            return pd.read_csv(uploaded)
        return pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Failed to read {uploaded.name}: {e}")
        return None


# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("<h1>Brand PPC Audit Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    '<p style="opacity:0.6; font-size:1.05rem; margin-bottom:1.5rem;">'
    "Comprehensive analytics for Sponsored Products, Brands & Display campaigns.</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# Sidebar — Data Source
with st.sidebar:
    st.markdown("### Data Source")
    st.markdown("Upload your Amazon Advertising reports below.")

    with st.expander("Sponsored Products (SP)", expanded=True):
        sp_search_file = st.file_uploader("SP Search Term Report", type=["csv", "xlsx"], key="sp_srch")
        sp_placement_file = st.file_uploader("SP Placement Report", type=["csv", "xlsx"], key="sp_plc")

    with st.expander("Sponsored Brands (SB)", expanded=True):
        sb_search_file = st.file_uploader("SB Search Term Report", type=["csv", "xlsx"], key="sb_srch")
        sb_placement_file = st.file_uploader("SB Placement Report", type=["csv", "xlsx"], key="sb_plc")

    with st.expander("Sponsored Display (SD)", expanded=True):
        sd_report_file = st.file_uploader("SD Campaign Report", type=["csv", "xlsx"], key="sd_rep")

    st.markdown("---")
    run_audit = st.button("Run Audit", type="primary", use_container_width=True)

if run_audit:
    files = [sp_search_file, sp_placement_file, sb_search_file, sb_placement_file, sd_report_file]
    if all(x is None for x in files):
        st.error("Please upload at least one campaign report to proceed.")
        st.stop()

    with st.spinner("Processing campaign data..."):
        sp_search_raw = read_file(sp_search_file)
        sp_place_raw  = read_file(sp_placement_file)
        sb_search_raw = read_file(sb_search_file)
        sb_place_raw  = read_file(sb_placement_file)
        sd_raw        = read_file(sd_report_file)

        sp_search = add_metrics(normalize_report(sp_search_raw, "SP"))
        sp_place  = add_metrics(normalize_report(sp_place_raw,  "SP"))
        sb_search = add_metrics(normalize_report(sb_search_raw, "SB"))
        sb_place  = add_metrics(normalize_report(sb_place_raw,  "SB"))
        sd_data   = add_metrics(normalize_report(sd_raw, "SD"))

        sp_kpi = sp_search if not sp_search.empty else sp_place
        sb_kpi = sb_search if not sb_search.empty else sb_place
        combined = pd.concat([sp_kpi, sb_kpi, sd_data], ignore_index=True)

        if combined.empty:
            st.error("No valid advertising data found. Please ensure you are uploading the correct Amazon reports.")
            st.stop()
    

    if "Date" in combined.columns and pd.api.types.is_datetime64_any_dtype(combined["Date"]):
        mn, mx = combined["Date"].min(), combined["Date"].max()
        if pd.notna(mn) and pd.notna(mx):
            st.markdown(
                f'<div class="date-range-bar">Report Period: {mn.date()} to {mx.date()}</div>',
                unsafe_allow_html=True,
            )

    # KPI
    summary = kpi_summary(combined)
    units_val = int(combined["Units"].sum()) if "Units" in combined.columns else 0
    waste = summary["Waste Spend"]
    profit = summary["Sales"] - summary["Spend"]

    st.markdown("### Executive Summary")

    cols = st.columns(5)
    row1 = [
        ("Total Spend",  f"${summary['Spend']:,.2f}",      "#dc2626"),
        ("Total Sales",  f"${summary['Sales']:,.2f}",      "#059669"),
        ("Orders",       f"{summary['Orders']:,}",         "#2563eb"),
        ("Clicks",       f"{summary['Clicks']:,}",         "#0284c7"),
        ("Impressions",  f"{summary['Impressions']:,}",    "#475569"),
    ]
    for col, (lbl, val, clr) in zip(cols, row1):
        col.markdown(kpi_tile(lbl, val, clr), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Efficiency metrics
    cols2 = st.columns(5)
    row2 = [
        ("ACOS",  f"{summary['ACOS']:.2%}",   "#dc2626" if summary["ACOS"] > 0.3 else "#059669"),
        ("ROAS",  f"{summary['ROAS']:.2f}x",   "#059669" if summary["ROAS"] >= 3 else "#d97706"),
        ("CPC",   f"${summary['CPC']:.2f}",    "#2563eb"),
        ("CTR",   f"{summary['CTR']:.2%}",     "#0284c7"),
        ("CVR",   f"{summary['CVR']:.2%}",     "#059669"),
    ]
    for col, (lbl, val, clr) in zip(cols2, row2):
        col.markdown(kpi_tile(lbl, val, clr), unsafe_allow_html=True)

    st.markdown("---")

    # Tabs
    tab_sp, tab_sb, tab_sd, tab_trends, tab_export = st.tabs([
        "Sponsored Products",
        "Sponsored Brands",
        "Sponsored Display",
        "Trend Analysis",
        "Export",
    ])

    with tab_sp:
        st.markdown("## Sponsored Products Report")
        if not sp_search.empty:
            st.markdown("---")
            piv = render_pivot(sp_search, "Match Type", "SP — Match Type Data")
            render_spend_sales_line(sp_search, title="SP — Daily Spend vs Sales")
            render_charts(piv, "Match Type", "SP Match Type")
        else:
            st.info("No SP Search Term data uploaded.")

        if not sp_place.empty:
            st.markdown("---")
            piv = render_pivot(sp_place, "Placement", "SP — Placement Data")
            render_charts(piv, "Placement", "SP Placement")
        else:
            st.info("No SP Placement data uploaded.")

    with tab_sb:
        st.markdown("## Sponsored Brands Report")
        if not sb_search.empty:
            st.markdown("---")
            piv = render_pivot(sb_search, "Match Type", "SB — Match Type Data")
            render_spend_sales_line(sb_search, title="SB — Daily Spend vs Sales")
            render_charts(piv, "Match Type", "SB Match Type")
        else:
            st.info("No SB Search Term data uploaded.")

        if not sb_place.empty:
            st.markdown("---")
            piv = render_pivot(sb_place, "Placement", "SB — Placement Data")
            render_charts(piv, "Placement", "SB Placement")
        else:
            st.info("No SB Placement data uploaded.")

    with tab_sd:
        st.markdown("## Sponsored Display Report")
        if not sd_data.empty:
            st.markdown("---")
            grp = "Campaign" if "Campaign" in sd_data.columns and sd_data["Campaign"].nunique() > 1 else "Ad Type"
            piv = render_pivot(sd_data, grp, f"SD — {grp} Data")
            render_spend_sales_line(sd_data, title="SD — Daily Spend vs Sales")
            render_charts(piv, grp, f"SD {grp}")
        else:
            st.info("No Sponsored Display data uploaded.")

    with tab_trends:
        st.markdown("#### Ad Type Summary")
        datasets = {"Sponsored Products": sp_search, "Sponsored Brands": sb_search, "Sponsored Display": sd_data}
        rows = []
        for name, ds in datasets.items():
            if ds is not None and not ds.empty:
                s = kpi_summary(ds)
                u = int(ds["Units"].sum()) if "Units" in ds.columns else 0
                rows.append({
                    "Ad Type": name, "Sales": s["Sales"], "Spend": s["Spend"],
                    "Units": u, "Clicks": s["Clicks"], "Impressions": s["Impressions"],
                    "ACOS": s["ACOS"], "CTR": s["CTR"], "CVR": s["CVR"],
                    "CPC": s["CPC"], "ROAS": s["ROAS"],
                })
        if rows:
            ad_df = pd.DataFrame(rows)
            ts = ad_df["Spend"].sum()
            tsl = ad_df["Sales"].sum()
            ad_df["% Spend Share"] = ad_df["Spend"] / ts if ts > 0 else 0
            ad_df["% Sale Share"] = ad_df["Sales"] / tsl if tsl > 0 else 0
            gt = {
                "Ad Type": "Grand Total",
                "Sales": ad_df["Sales"].sum(), "Spend": ad_df["Spend"].sum(),
                "Units": ad_df["Units"].sum(), "Clicks": ad_df["Clicks"].sum(),
                "Impressions": ad_df["Impressions"].sum(),
                "ACOS": ad_df["Spend"].sum() / ad_df["Sales"].sum() if ad_df["Sales"].sum() > 0 else 0,
                "CTR": ad_df["Clicks"].sum() / ad_df["Impressions"].sum() if ad_df["Impressions"].sum() > 0 else 0,
                "CVR": 0,
                "CPC": ad_df["Spend"].sum() / ad_df["Clicks"].sum() if ad_df["Clicks"].sum() > 0 else 0,
                "ROAS": ad_df["Sales"].sum() / ad_df["Spend"].sum() if ad_df["Spend"].sum() > 0 else 0,
                "% Spend Share": 1.0, "% Sale Share": 1.0,
            }
            ad_df = pd.concat([ad_df, pd.DataFrame([gt])], ignore_index=True)
            display_cols = ["Ad Type", "Sales", "Spend", "Units", "Clicks", "Impressions",
                            "ACOS", "CTR", "CVR", "CPC", "ROAS", "% Spend Share", "% Sale Share"]
            ad_df = ad_df[[c for c in display_cols if c in ad_df.columns]]
            st.dataframe(
                ad_df.style.format({k: v for k, v in AD_TYPE_SUMMARY_FORMAT.items() if k in ad_df.columns}),
                use_container_width=True, hide_index=True,
            )

        st.markdown("#### Wasted Ad Spend")
        wrows = []
        for name, ds in datasets.items():
            if ds is not None and not ds.empty:
                tot_spend = ds["Spend"].sum()
                wasted_spend = ds["Waste Spend"].sum()
                tot_clicks = ds["Clicks"].sum()
                wasted_clicks = ds.loc[ds["Orders"] == 0, "Clicks"].sum() if "Orders" in ds.columns else 0
                wrows.append({
                    "Ad Type": name,
                    "Total Spend": tot_spend,
                    "Wasted Spend": wasted_spend,
                    "% Wasted Spend": wasted_spend / tot_spend if tot_spend > 0 else 0,
                    "Clicks": tot_clicks,
                    "Wasted Clicks": wasted_clicks,
                    "% Wasted Clicks": wasted_clicks / tot_clicks if tot_clicks > 0 else 0,
                })
        if wrows:
            w_df = pd.DataFrame(wrows)
            gt_w = {
                "Ad Type": "Grand Total",
                "Total Spend": w_df["Total Spend"].sum(),
                "Wasted Spend": w_df["Wasted Spend"].sum(),
                "% Wasted Spend": w_df["Wasted Spend"].sum() / w_df["Total Spend"].sum() if w_df["Total Spend"].sum() > 0 else 0,
                "Clicks": w_df["Clicks"].sum(),
                "Wasted Clicks": w_df["Wasted Clicks"].sum(),
                "% Wasted Clicks": w_df["Wasted Clicks"].sum() / w_df["Clicks"].sum() if w_df["Clicks"].sum() > 0 else 0,
            }
            w_df = pd.concat([w_df, pd.DataFrame([gt_w])], ignore_index=True)
            st.dataframe(
                w_df.style.format({k: v for k, v in WASTED_FORMAT.items() if k in w_df.columns}),
                use_container_width=True, hide_index=True,
            )

        st.markdown("---")
     
    with tab_export:
        st.markdown("### Export Analysis")
        export_dict = {}
        if not sp_search.empty:
            export_dict["SP_Match_Type"] = pivot(sp_search, "Match Type", add_grand_total=True)
        if not sp_place.empty:
            export_dict["SP_Placement"] = pivot(sp_place, "Placement", add_grand_total=True)
        if not sb_search.empty:
            export_dict["SB_Match_Type"] = pivot(sb_search, "Match Type", add_grand_total=True)
        if not sb_place.empty:
            export_dict["SB_Placement"] = pivot(sb_place, "Placement", add_grand_total=True)
        if not sd_data.empty:
            grp = "Campaign" if "Campaign" in sd_data.columns else "Ad Type"
            export_dict["SD_Data"] = pivot(sd_data, grp, add_grand_total=True)

        if export_dict:
            st.download_button(
                label="Download Complete Analysis (Excel)",
                data=export_excel(export_dict),
                file_name="Amazon_PPC_Audit_Analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.info("No data available to export.")

else:
    st.info("Upload campaign reports in the sidebar and click **Run Audit** to begin.")