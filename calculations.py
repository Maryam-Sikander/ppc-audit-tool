import pandas as pd
import numpy as np
import io
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows



def strip_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def first_present(df, candidates):
    cols = {c.lower(): c for c in df.columns}
    for c in candidates:
        lc = c.lower()
        if lc in cols:
            return cols[lc]
    return None

def clean_money_pct_numeric(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
         .str.replace(r'[\$,]', '', regex=True)
         .str.replace('%', '', regex=False)
         .replace({'': np.nan, 'nan': np.nan})
         .astype(float)
    )

def parse_date_col(df):

    candidates = [
        "Date", "date", "day", "report date", "transaction date", "report_date",
        "Start Date", "End Date", "start date", "end date", "start_date", "end_date"
    ]
    for cand in candidates:
        if cand in df.columns:
            try:
                return pd.to_datetime(df[cand], errors="coerce")
            except Exception:
                # try next candidate
                pass
    # no explicit date-like column found
    return None

def normalize_report(df: pd.DataFrame, ad_type_hint: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["Ad Type","Date","Campaign","Match Type","Placement","Targeting","Search Term","Clicks","Impressions","Spend","Sales","Orders"])

    df = strip_cols(df)

    clicks_col = first_present(df, [
        "Clicks", "clicks"
    ])
    impr_col = first_present(df, [
        "Impressions", "Viewable Impressions", "impressions"
    ])
    spend_col = first_present(df, [
        "Spend", "Cost", "Spend (USD)", "Total Spend"
    ])
    sales_col = first_present(df, [
        "14 Day Total Sales", "14 Day Total Sales ", "14 Day Total Sales - (Click)",
        "7 Day Total Sales", "14-Day Total Sales", "14 Day Total Sales (#)",
        "Total Sales", "Sales", "sales", "14 Day Total Sales- (Click)"
    ])
    orders_col = first_present(df, [
        "14 Day Total Orders (#)", "14 Day Total Orders", "14 Day Total Orders (#) - (Click)",
        "7 Day Total Orders (#)", "14-Day Total Orders (#)", "14-Day Total Orders",
        "Total Orders", "Orders", "orders", "14 Day Total Orders (#) "
    ])
    units_col = first_present(df, [
        "14 Day Total Units (#)", "14 Day Total Units", "7 Day Total Units (#)", 
        "14-Day Total Units (#)", "Total Units", "Units", "units", "Quantity"
    ])
    match_col = first_present(df, ["Match Type", "match type", "MatchType"])
    plac_col = first_present(df, ["Placement", "placement"])
    camp_col = first_present(df, ["Campaign", "Campaign Name", "campaign"])
    targeting_col = first_present(df, ["Targeting", "targeting", "Targeting Type"])
    search_term_col = first_present(df, ["Customer Search Term", "Search Term", "customer search term", "search term", "Query"])
    date_series = parse_date_col(df)

    required_missing = [n for n, v in {
        "Clicks": clicks_col, "Impressions": impr_col, "Spend": spend_col,
        "Sales": sales_col, "Orders": orders_col
    }.items() if v is None]

    if required_missing:
        return pd.DataFrame(columns=["Ad Type","Date","Campaign","Match Type","Placement","Targeting","Search Term","Clicks","Impressions","Spend","Sales","Orders"])

    out = pd.DataFrame()
    out["Ad Type"] = ad_type_hint
    out["Date"] = date_series if date_series is not None else pd.NaT
    out["Campaign"] = df[camp_col] if camp_col else ""
    out["Match Type"] = df[match_col] if match_col else ""
    out["Placement"] = df[plac_col] if plac_col else ""
    out["Targeting"] = df[targeting_col] if targeting_col else ""
    out["Search Term"] = df[search_term_col] if search_term_col else ""

    # Replace "-", empty, and blank Match Type values with "Auto"
    out["Match Type"] = out["Match Type"].astype(str).str.strip()
    out["Match Type"] = out["Match Type"].replace({"-": "Auto", "": "Auto", "nan": "Auto"})
    out.loc[out["Match Type"].isna(), "Match Type"] = "Auto"

    out["Clicks"] = clean_money_pct_numeric(df[clicks_col]).fillna(0)
    out["Impressions"] = clean_money_pct_numeric(df[impr_col]).fillna(0)
    out["Spend"] = clean_money_pct_numeric(df[spend_col]).fillna(0)
    out["Sales"] = clean_money_pct_numeric(df[sales_col]).fillna(0)
    out["Orders"] = clean_money_pct_numeric(df[orders_col]).fillna(0)
    out["Units"]  = clean_money_pct_numeric(df[units_col]).fillna(0)

    if "Wasted Spend" in df.columns:
        ws = clean_money_pct_numeric(df["Wasted Spend"])
        if "Spend" in out.columns:
            out["Waste Spend"] = np.where(out["Orders"] == 0, out["Spend"], 0.0)
            out["Waste Spend"] = np.where(ws > 0, ws, out["Waste Spend"])
        else:
            out["Waste Spend"] = ws
    else:
        out["Waste Spend"] = np.where(out["Orders"] == 0, out["Spend"], 0.0)

    for c in ["Clicks", "Impressions", "Spend", "Sales", "Orders", "Units", "Waste Spend"]:
        if c not in out.columns:
            out[c] = 0.0
    return out


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()
    df["CPC"]  = np.where(df["Clicks"] > 0, df["Spend"] / df["Clicks"], 0.0)
    df["CTR"]  = np.where(df["Impressions"] > 0, df["Clicks"] / df["Impressions"], 0.0)
    df["CVR"]  = np.where(df["Clicks"] > 0, df["Orders"] / df["Clicks"], 0.0)
    df["ACOS"] = np.where(df["Sales"] > 0, df["Spend"] / df["Sales"], 0.0)
    df["ROAS"] = np.where(df["Spend"] > 0, df["Sales"] / df["Spend"], 0.0)
    df["CAC"]  = np.where(df["Orders"] > 0, df["Spend"] / df["Orders"], 0.0)
    df["Waste Spend"] = np.where(df["Orders"] == 0, df["Spend"], 0.0)
    return df

def kpi_summary(df: pd.DataFrame) -> dict:
  
    tot_clicks = df["Clicks"].sum()
    tot_impr   = df["Impressions"].sum()
    tot_spend  = df["Spend"].sum()
    tot_sales  = df["Sales"].sum()
    tot_orders = df["Orders"].sum()
    tot_waste  = df["Waste Spend"].sum()

    # calculations
    cpc = (tot_spend / tot_clicks) if tot_clicks > 0 else 0.0
    ctr = (tot_clicks / tot_impr) if tot_impr > 0 else 0.0
    cvr = (tot_orders / tot_clicks) if tot_clicks > 0 else 0.0
    acos = (tot_spend / tot_sales) if tot_sales > 0 else 0.0
    roas = (tot_sales / tot_spend) if tot_spend > 0 else 0.0
    cac = (tot_spend / tot_orders) if tot_orders > 0 else 0.0

    return {
        "Clicks": int(tot_clicks),
        "Impressions": int(tot_impr),
        "Spend": float(tot_spend),
        "Sales": float(tot_sales),
        "Orders": int(tot_orders),
        "Waste Spend": float(tot_waste),
        "CPC": float(cpc),
        "CTR": float(ctr),
        "CVR": float(cvr),
        "ACOS": float(acos),
        "ROAS": float(roas),
        "CAC": float(cac),
    }

def pivot(df: pd.DataFrame, by: str, values=None, add_grand_total: bool = False) -> pd.DataFrame:
    if values is None:
        values = ["Impressions","Clicks","Spend","Sales","Units","Orders","Waste Spend","CPC","CTR","CVR","ACOS","ROAS","CAC"]
    for v in values:
        if v not in df.columns:
            df = df.copy()
            df[v] = 0.0
    if df is None or df.empty:
        return pd.DataFrame(columns=[by]+values)
    sum_cols = [c for c in values if c in ["Impressions","Clicks","Spend","Sales","Units","Orders","Waste Spend"]]
    g = df.groupby(by, dropna=False)[sum_cols].sum().reset_index()
    # ratio metrics from aggregated sums
    g["CPC"]  = np.where(g["Clicks"]>0, g["Spend"]/g["Clicks"], 0.0)
    g["CTR"]  = np.where(g["Impressions"]>0, g["Clicks"]/g["Impressions"], 0.0)
    g["CVR"]  = np.where(g["Clicks"]>0, g["Orders"]/g["Clicks"], 0.0)
    g["ACOS"] = np.where(g["Sales"]>0, g["Spend"]/g["Sales"], 0.0)
    g["ROAS"] = np.where(g["Spend"]>0, g["Sales"]/g["Spend"], 0.0)
    g["CAC"]  = np.where(g["Orders"]>0, g["Spend"]/g["Orders"], 0.0)
    # Percentage share cols
    total_spend = g["Spend"].sum()
    total_sales = g["Sales"].sum()
    g["% Adspend"] = np.where(total_spend > 0, g["Spend"] / total_spend, 0.0)
    g["% Ad Sale"] = np.where(total_sales > 0, g["Sales"] / total_sales, 0.0)
    if add_grand_total and not g.empty:
        totals = {by: "Grand Total"}
        for c in sum_cols:
            totals[c] = g[c].sum()
        totals["CPC"] = totals["Spend"] / totals["Clicks"] if totals.get("Clicks", 0) > 0 else 0.0
        totals["CTR"] = totals["Clicks"] / totals["Impressions"] if totals.get("Impressions", 0) > 0 else 0.0
        totals["CVR"] = totals["Orders"] / totals["Clicks"] if totals.get("Clicks", 0) > 0 else 0.0
        totals["ACOS"] = totals["Spend"] / totals["Sales"] if totals.get("Sales", 0) > 0 else 0.0
        totals["ROAS"] = totals["Sales"] / totals["Spend"] if totals.get("Spend", 0) > 0 else 0.0
        totals["CAC"] = totals["Spend"] / totals["Orders"] if totals.get("Orders", 0) > 0 else 0.0
        totals["% Adspend"] = 1.0
        totals["% Ad Sale"] = 1.0
        grand_row = pd.DataFrame([totals])
        g = pd.concat([g, grand_row], ignore_index=True)
    return g

def export_excel(dfs: dict) -> bytes:
  
    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    ws.append(["Amazon Ads – PPC Audit Export"])
    ws.append(["All values aggregated by the specified keys. Currency in same units as input."])
    ws.append([])

    for name, df in dfs.items():
        sh = wb.create_sheet(name[:31])
        for r in dataframe_to_rows(df, index=False, header=True):
            sh.append(r)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
