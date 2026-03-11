import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from scripts.config import Theme
from scripts.utils import format_number, format_currency, format_percentage, format_decimal



def plot_comparison_bars(df: pd.DataFrame, 
                         x_col: str, 
                         y_cols: list, 
                         title: str,
                         colors: list = None) -> go.Figure:

    if df is None or df.empty:
        return go.Figure()
    
    if colors is None:
        colors = Theme.CHART_COLORS
    
    fig = go.Figure()
    
    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Bar(
                name=col,
                x=df[x_col],
                y=df[col],
                marker_color=colors[i % len(colors)],
                text=df[col].apply(lambda x: format_number(x) if col in ['Spend', 'Sales', 'Clicks', 'Impressions'] else format_percentage(x) if 'CTR' in col or 'CVR' in col else f"{x:.2f}"),
                textposition='outside'
            ))
    
    fig.update_layout(
        title=title,
        barmode='group',
        height=400,
        xaxis_title=x_col,
        yaxis_title="Value",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    
    return fig



def plot_donut_chart(labels: list, values: list, title: str) -> go.Figure:

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=Theme.CHART_COLORS,
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title=title,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        showlegend=True
    )
    
    return fig



def plot_funnel(impressions: float, clicks: float, orders: float) -> go.Figure:

    fig = go.Figure(go.Funnel(
        y = ["Impressions", "Clicks", "Orders"],
        x = [impressions, clicks, orders],
        textposition = "inside",
        textinfo = "value+percent initial",
        marker = {"color": [Theme.COLORS['primary'], Theme.COLORS['secondary'], Theme.COLORS['success']]}
    ))
    
    fig.update_layout(
        title="Conversion Funnel",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    
    return fig



def plot_gauge(value: float, 
               title: str, 
               max_val: float = 1.0,
               threshold_good: float = 0.7,
               threshold_bad: float = 0.3) -> go.Figure:
   
    
    normalized_value = value / max_val if max_val > 0 else 0
    
    if normalized_value >= threshold_good:
        color = Theme.COLORS['success']
    elif normalized_value <= threshold_bad:
        color = Theme.COLORS['danger']
    else:
        color = Theme.COLORS['warning']
    
    display_value = value * 100 if max_val == 1.0 else value
    display_max = max_val * 100 if max_val == 1.0 else max_val
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = display_value,
        title = {'text': title, 'font': {'size': 16, 'color': Theme.COLORS['text']}},
        number = {'font': {'color': Theme.COLORS['text']}},
        gauge = {
            'axis': {'range': [None, display_max], 'tickfont': {'color': Theme.COLORS['text']}},
            'bar': {'color': color},
            'bgcolor': '#e2e8f0',
            'borderwidth': 2,
            'bordercolor': '#cbd5e1',
            'steps': [
                {'range': [0, threshold_bad * display_max], 'color': '#fee2e2'},
                {'range': [threshold_good * display_max, display_max], 'color': '#dcfce7'}
            ]
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    
    return fig



def plot_scatter_efficiency(df: pd.DataFrame) -> go.Figure:

    if df is None or df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df,
        x="ACOS",
        y="ROAS",
        size="Spend",
        color="Ad Type" if "Ad Type" in df.columns else None,
        hover_data=["Clicks", "Sales", "Orders"] if all(c in df.columns for c in ["Clicks", "Sales", "Orders"]) else None,
        title="Efficiency Matrix (ACOS vs ROAS)",
        color_discrete_map={"SP": Theme.COLORS['primary'], "SB": Theme.COLORS['success'], "SD": Theme.COLORS['info']},
        size_max=60
    )
    
    # Add benchmark lines
    fig.add_hline(y=3, line_dash="dash", line_color=Theme.COLORS['success'], opacity=0.5, annotation_text="Target ROAS: 3.0x")
    fig.add_vline(x=0.3, line_dash="dash", line_color=Theme.COLORS['warning'], opacity=0.5, annotation_text="Target ACOS: 30%")
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        showlegend=True,
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    
    return fig



def plot_quarterly_trends(df: pd.DataFrame, metrics: list) -> go.Figure:
   
    if df is None or df.empty or 'Quarter' not in df.columns:
        return go.Figure()
    
    fig = go.Figure()
    
    colors = Theme.CHART_COLORS
    
    for i, metric in enumerate(metrics):
        if metric in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Quarter'],
                y=df[metric],
                name=metric,
                mode='lines+markers',
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=10)
            ))
    
    fig.update_layout(
        title="Quarterly Performance Trends",
        xaxis_title="Quarter",
        yaxis_title="Value",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    
    return fig



def plot_ad_type_comparison(df: pd.DataFrame) -> go.Figure:
 
    if df is None or df.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Spend Comparison', 'Sales Comparison', 'ACOS Comparison', 'ROAS Comparison'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Spend
    fig.add_trace(go.Bar(
        x=df["Ad Type"], 
        y=df["Spend"],
        name="Spend",
        marker_color=Theme.COLORS['primary'],
        text=df["Spend"].apply(format_currency),
        textposition='outside'
    ), row=1, col=1)
    
    # Sales
    fig.add_trace(go.Bar(
        x=df["Ad Type"],
        y=df["Sales"],
        name="Sales",
        marker_color=Theme.COLORS['success'],
        text=df["Sales"].apply(format_currency),
        textposition='outside'
    ), row=1, col=2)
    
    # ACOS
    fig.add_trace(go.Bar(
        x=df["Ad Type"],
        y=df["ACOS"]*100,
        name="ACOS %",
        marker_color=Theme.COLORS['danger'],
        text=df["ACOS"].apply(format_percentage),
        textposition='outside'
    ), row=2, col=1)
    
    # ROAS
    fig.add_trace(go.Bar(
        x=df["Ad Type"],
        y=df["ROAS"],
        name="ROAS",
        marker_color=Theme.COLORS['info'],
        text=df["ROAS"].apply(format_decimal),
        textposition='outside'
    ), row=2, col=2)
    
    fig.update_yaxes(title_text="Spend ($)", row=1, col=1)
    fig.update_yaxes(title_text="Sales ($)", row=1, col=2)
    fig.update_yaxes(title_text="ACOS (%)", row=2, col=1)
    fig.update_yaxes(title_text="ROAS (x)", row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Ad Type Performance Comparison",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    
    return fig


def plot_match_type_analysis(df: pd.DataFrame, ad_type: str) -> go.Figure:
   
    if df is None or df.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            f'{ad_type} Clicks by Match Type',
            f'{ad_type} CTR by Match Type',
            f'{ad_type} CVR by Match Type',
            f'{ad_type} CPC by Match Type'
        )
    )
    
    colors = Theme.CHART_COLORS
    
    # Clicks
    fig.add_trace(go.Bar(
        x=df["Match Type"],
        y=df["Clicks"],
        marker_color=colors[0],
        name="Clicks",
        text=df["Clicks"].apply(format_number),
        textposition='outside'
    ), row=1, col=1)
    
    # CTR
    fig.add_trace(go.Bar(
        x=df["Match Type"],
        y=df["CTR"]*100,
        marker_color=colors[1],
        name="CTR %",
        text=df["CTR"].apply(format_percentage),
        textposition='outside'
    ), row=1, col=2)
    
    # CVR
    fig.add_trace(go.Bar(
        x=df["Match Type"],
        y=df["CVR"]*100,
        marker_color=colors[2],
        name="CVR %",
        text=df["CVR"].apply(format_percentage),
        textposition='outside'
    ), row=2, col=1)
    
    # CPC
    fig.add_trace(go.Bar(
        x=df["Match Type"],
        y=df["CPC"],
        marker_color=colors[3],
        name="CPC",
        text=df["CPC"].apply(format_currency),
        textposition='outside'
    ), row=2, col=2)
    
    fig.update_yaxes(title_text="Clicks", row=1, col=1)
    fig.update_yaxes(title_text="CTR (%)", row=1, col=2)
    fig.update_yaxes(title_text="CVR (%)", row=2, col=1)
    fig.update_yaxes(title_text="CPC ($)", row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    
    return fig



def plot_brand_share_evolution(df: pd.DataFrame) -> go.Figure:

    if df is None or df.empty or 'Quarter' not in df.columns:
        return go.Figure()
    
    fig = go.Figure()
    
    # Impressions Share
    fig.add_trace(go.Scatter(
        x=df['Quarter'],
        y=df['Impressions Share'] * 100,
        name='Impressions Share',
        mode='lines+markers',
        line=dict(color=Theme.COLORS['primary'], width=3),
        marker=dict(size=10)
    ))
    
    # Clicks Share
    fig.add_trace(go.Scatter(
        x=df['Quarter'],
        y=df['Clicks Share'] * 100,
        name='Clicks Share',
        mode='lines+markers',
        line=dict(color=Theme.COLORS['info'], width=3),
        marker=dict(size=10)
    ))
    
    # Purchases Share
    fig.add_trace(go.Scatter(
        x=df['Quarter'],
        y=df['Purchases Share'] * 100,
        name='Purchases Share',
        mode='lines+markers',
        line=dict(color=Theme.COLORS['success'], width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Brand Share Evolution Across Quarters",
        xaxis_title="Quarter",
        yaxis_title="Brand Share (%)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    
    return fig



def plot_wasted_spend(wasted: float, efficient: float) -> go.Figure:

    labels = ['Efficient Spend', 'Wasted Spend']
    values = [efficient, wasted]
    colors = [Theme.COLORS['success'], Theme.COLORS['danger']]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Spend Efficiency Analysis",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    
    return fig



def plot_heatmap(df: pd.DataFrame, title: str) -> go.Figure:

    if df is None or df.empty:
        return go.Figure()
    
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale='RdYlGn',
        text=df.values,
        texttemplate='%{text:.2f}',
        textfont={"size":10, "color": "white"}
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    
    return fig



def plot_spend_vs_sales(df: pd.DataFrame, group_col: str, title: str) -> go.Figure:
 
    if df is None or df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Spend',
        x=df[group_col],
        y=df['Spend'],
        marker_color=Theme.COLORS['danger'],
        text=df['Spend'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside'
    ))
    fig.add_trace(go.Bar(
        name='Sales',
        x=df[group_col],
        y=df['Sales'],
        marker_color=Theme.COLORS['success'],
        text=df['Sales'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside'
    ))
    fig.update_layout(
        title=title,
        barmode='group',
        height=420,
        xaxis_title=group_col,
        yaxis_title="Amount ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    )
    return fig



def plot_spend_distribution(df: pd.DataFrame, group_col: str, metric: str, title: str) -> go.Figure:
  
    if df is None or df.empty or metric not in df.columns:
        return go.Figure()

    # Filter out Grand Total 
    chart_df = df[df[group_col] != "Grand Total"].copy()

    fig = go.Figure(data=[go.Pie(
        labels=chart_df[group_col],
        values=chart_df[metric],
        hole=.45,
        marker_colors=Theme.CHART_COLORS,
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='%{label}<br>' + metric + ': $%{value:,.2f}<br>Share: %{percent}<extra></extra>'
    )])
    fig.update_layout(
        title=title,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig



def plot_acos_comparison(df: pd.DataFrame, group_col: str, title: str) -> go.Figure:

    if df is None or df.empty:
        return go.Figure()

    chart_df = df[df[group_col] != "Grand Total"].copy()

    colors = [Theme.COLORS['success'] if a < 0.30 else Theme.COLORS['warning'] if a < 0.50 else Theme.COLORS['danger'] 
              for a in chart_df['ACOS']]

    fig = go.Figure(go.Bar(
        y=chart_df[group_col],
        x=chart_df['ACOS'] * 100,
        orientation='h',
        marker_color=colors,
        text=chart_df['ACOS'].apply(lambda x: f'{x:.1%}'),
        textposition='outside'
    ))
    fig.add_vline(x=30, line_dash="dash", line_color=Theme.COLORS['danger'], opacity=0.6,
                  annotation_text="Target: 30%", annotation_position="top right")
    fig.update_layout(
        title=title,
        height=350,
        xaxis_title="ACOS (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
        yaxis=dict(showgrid=False)
    )
    return fig



def plot_efficiency_metrics(df: pd.DataFrame, group_col: str, title: str) -> go.Figure:
 
    if df is None or df.empty:
        return go.Figure()

    chart_df = df[df[group_col] != "Grand Total"].copy()

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('CPC ($)', 'CTR (%)', 'CVR (%)'),
        horizontal_spacing=0.08
    )

    # CPC
    fig.add_trace(go.Bar(
        x=chart_df[group_col], y=chart_df['CPC'],
        marker_color=Theme.CHART_COLORS[0],
        text=chart_df['CPC'].apply(lambda x: f'${x:.2f}'),
        textposition='outside', name='CPC', showlegend=False
    ), row=1, col=1)

    # CTR
    fig.add_trace(go.Bar(
        x=chart_df[group_col], y=chart_df['CTR'] * 100,
        marker_color=Theme.CHART_COLORS[1],
        text=chart_df['CTR'].apply(lambda x: f'{x:.2%}'),
        textposition='outside', name='CTR', showlegend=False
    ), row=1, col=2)

    # CVR
    fig.add_trace(go.Bar(
        x=chart_df[group_col], y=chart_df['CVR'] * 100,
        marker_color=Theme.CHART_COLORS[2],
        text=chart_df['CVR'].apply(lambda x: f'{x:.2%}'),
        textposition='outside', name='CVR', showlegend=False
    ), row=1, col=3)

    fig.update_layout(
        title=title,
        height=380,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text']
    )
    for i in range(1, 4):
        fig.update_xaxes(showgrid=False, row=1, col=i)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=1, col=i)

    return fig



def plot_wasted_spend_bar(df: pd.DataFrame, group_col: str, title: str) -> go.Figure:

    if df is None or df.empty:
        return go.Figure()

    chart_df = df[df[group_col] != "Grand Total"].copy()
    chart_df["Efficient Spend"] = chart_df["Spend"] - chart_df["Waste Spend"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Efficient Spend',
        x=chart_df[group_col],
        y=chart_df['Efficient Spend'],
        marker_color=Theme.COLORS['success'],
        text=chart_df['Efficient Spend'].apply(lambda x: f'${x:,.0f}'),
        textposition='inside'
    ))
    fig.add_trace(go.Bar(
        name='Wasted Spend',
        x=chart_df[group_col],
        y=chart_df['Waste Spend'],
        marker_color=Theme.COLORS['danger'],
        text=chart_df['Waste Spend'].apply(lambda x: f'${x:,.0f}'),
        textposition='inside'
    ))
    fig.update_layout(
        title=title,
        barmode='stack',
        height=400,
        xaxis_title=group_col,
        yaxis_title="Spend ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=Theme.COLORS['text'],
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    )
    return fig