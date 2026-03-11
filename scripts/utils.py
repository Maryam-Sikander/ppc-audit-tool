import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any
from typing import Tuple




def format_currency(value: Union[float, int], currency_symbol: str = "$") -> str:
    if pd.isna(value) or value is None:
        return f"{currency_symbol}0.00"
    
    try:
        value = float(value)
        if abs(value) >= 1_000_000:
            return f"{currency_symbol}{value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{currency_symbol}{value/1_000:.2f}K"
        else:
            return f"{currency_symbol}{value:.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"


def format_percentage(value: Union[float, int], decimals: int = 2) -> str:
    if pd.isna(value) or value is None:
        return "0.00%"
    
    try:
        value = float(value)
        return f"{value * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def format_decimal(value: Union[float, int], decimals: int = 2) -> str:
    if pd.isna(value) or value is None:
        return "0.00"
    
    try:
        value = float(value)
        return f"{value:.{decimals}f}"
    except (ValueError, TypeError):
        return "0.00"


def format_number(value: Union[float, int]) -> str:
    if pd.isna(value) or value is None:
        return "0"
    
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.2f}K"
        else:
            return f"{int(value):,}"
    except (ValueError, TypeError):
        return "0"


def format_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:


    if df is None or df.empty:
        return df
    
    display_df = df.copy()
    
    for col in display_df.columns:
        # Skip non-numeric columns
        if not pd.api.types.is_numeric_dtype(display_df[col]):
            continue
        
        col_lower = col.lower()
        
        # Currency columns
        if any(keyword in col_lower for keyword in ['spend', 'sales', 'revenue', 'cost', 'cpc', 'cpm']):
            display_df[col] = display_df[col].apply(lambda x: format_currency(x))
        
        # Percentage columns
        elif any(keyword in col_lower for keyword in ['acos', 'roas', 'ctr', 'cvr', 'rate', '%', 'share']):
            # Check if values are already in percentage format (>1) or decimal format (<1)
            if display_df[col].max() <= 1:
                display_df[col] = display_df[col].apply(lambda x: format_percentage(x))
            else:
                display_df[col] = display_df[col].apply(lambda x: format_percentage(x/100))
        
        # Count columns
        elif any(keyword in col_lower for keyword in ['clicks', 'impressions', 'orders', 'sessions', 'units', 'count']):
            display_df[col] = display_df[col].apply(lambda x: format_number(x))
        
        # Default decimal formatting
        else:
            display_df[col] = display_df[col].apply(lambda x: format_decimal(x))
    
    return display_df




def safe_divide(numerator: Union[float, int], denominator: Union[float, int], 
                default: float = 0.0) -> float:

    try:
        if pd.isna(numerator) or pd.isna(denominator):
            return default
        
        denominator = float(denominator)
        if denominator == 0:
            return default
        
        return float(numerator) / denominator
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def calculate_acos(spend: float, sales: float) -> float:
    #Calculate ACOS 
    return safe_divide(spend, sales, 0.0)


def calculate_roas(sales: float, spend: float) -> float:
    # Calculate ROAS
    return safe_divide(sales, spend, 0.0)


def calculate_ctr(clicks: float, impressions: float) -> float:
    # CTR
    return safe_divide(clicks, impressions, 0.0)


def calculate_cvr(orders: float, clicks: float) -> float:
    # Calculate CVR (Conversion Rate)"""
    return safe_divide(orders, clicks, 0.0)


def calculate_cpc(spend: float, clicks: float) -> float:
    """Calculate CPC (Cost Per Click)"""
    return safe_divide(spend, clicks, 0.0)


def calculate_cpm(spend: float, impressions: float) -> float:
    """Calculate CPM (Cost Per 1000 Impressions)"""
    return safe_divide(spend * 1000, impressions, 0.0)


def calculate_efficiency_score(acos: float, target_acos: float = 0.30) -> str:
    """
    Calculate efficiency score based on ACOS vs target
    
    Args:
        acos: Actual ACOS
        target_acos: Target ACOS (default 30%)
    
    Returns:
        Efficiency rating string
    """
    if pd.isna(acos) or acos == 0:
        return "N/A"
    
    ratio = acos / target_acos
    
    if ratio <= 0.7:
        return "Excellent"
    elif ratio <= 1.0:
        return "Good"
    elif ratio <= 1.3:
        return "Fair"
    else:
        return "Poor"


def calculate_performance_tier(roas: float) -> str:
    """
    Categorize performance based on ROAS
    
    Args:
        roas: Return on Ad Spend
    
    Returns:
        Performance tier string
    """
    if pd.isna(roas) or roas == 0:
        return "N/A"
    
    if roas >= 5.0:
        return "Elite"
    elif roas >= 3.0:
        return "Strong"
    elif roas >= 2.0:
        return "Average"
    elif roas >= 1.0:
        return "Weak"
    else:
        return "Unprofitable"




def clean_numeric_column(series: pd.Series) -> pd.Series:
    """
    Clean and convert a series to numeric, handling common issues
    
    Args:
        series: Input pandas Series
    
    Returns:
        Cleaned numeric Series
    """
    # Remove currency symbols, commas, and percentage signs
    if series.dtype == 'object':
        series = series.astype(str).str.replace('$', '', regex=False)
        series = series.str.replace(',', '', regex=False)
        series = series.str.replace('%', '', regex=False)
        series = series.str.strip()
    
    # Convert to numeric
    return pd.to_numeric(series, errors='coerce').fillna(0)


def aggregate_metrics(df: pd.DataFrame, group_by: List[str]) -> pd.DataFrame:
    """
    Aggregate metrics by specified columns
    
    Args:
        df: Input dataframe
        group_by: List of columns to group by
    
    Returns:
        Aggregated dataframe with calculated metrics
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Define aggregation rules
    agg_dict = {}
    
    # Sum columns
    sum_cols = ['Spend', 'Sales', 'Clicks', 'Impressions', 'Orders']
    for col in sum_cols:
        if col in df.columns:
            agg_dict[col] = 'sum'
    
    # Aggregate
    if not agg_dict:
        return df
    
    result = df.groupby(group_by, as_index=False).agg(agg_dict)
    
    # Calculate derived metrics
    if 'Spend' in result.columns and 'Sales' in result.columns:
        result['ACOS'] = result.apply(lambda x: calculate_acos(x['Spend'], x['Sales']), axis=1)
        result['ROAS'] = result.apply(lambda x: calculate_roas(x['Sales'], x['Spend']), axis=1)
    
    if 'Clicks' in result.columns and 'Impressions' in result.columns:
        result['CTR'] = result.apply(lambda x: calculate_ctr(x['Clicks'], x['Impressions']), axis=1)
    
    if 'Orders' in result.columns and 'Clicks' in result.columns:
        result['CVR'] = result.apply(lambda x: calculate_cvr(x['Orders'], x['Clicks']), axis=1)
    
    if 'Spend' in result.columns and 'Clicks' in result.columns:
        result['CPC'] = result.apply(lambda x: calculate_cpc(x['Spend'], x['Clicks']), axis=1)
    
    return result


def identify_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """
    Identify outliers in a dataframe column
    
    Args:
        df: Input dataframe
        column: Column to analyze
        method: Method to use ('iqr' or 'zscore')
    
    Returns:
        Dataframe with outlier flag column
    """
    if df is None or df.empty or column not in df.columns:
        return df
    
    result = df.copy()
    
    if method == 'iqr':
        Q1 = result[column].quantile(0.25)
        Q3 = result[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        result[f'{column}_outlier'] = (
            (result[column] < lower_bound) | (result[column] > upper_bound)
        )
    
    elif method == 'zscore':
        mean = result[column].mean()
        std = result[column].std()
        
        if std > 0:
            result[f'{column}_zscore'] = (result[column] - mean) / std
            result[f'{column}_outlier'] = abs(result[f'{column}_zscore']) > 3
        else:
            result[f'{column}_outlier'] = False
    
    return result


def get_top_n(df: pd.DataFrame, metric: str, n: int = 10, ascending: bool = False) -> pd.DataFrame:
    """
    Get top N rows based on a metric
    
    Args:
        df: Input dataframe
        metric: Column to sort by
        n: Number of rows to return
        ascending: Sort order
    
    Returns:
        Top N dataframe
    """
    if df is None or df.empty or metric not in df.columns:
        return pd.DataFrame()
    
    return df.nlargest(n, metric) if not ascending else df.nsmallest(n, metric)


def calculate_contribution_percentage(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Calculate each row's percentage contribution to total
    
    Args:
        df: Input dataframe
        column: Column to calculate contribution for
    
    Returns:
        Series with contribution percentages
    """
    if df is None or df.empty or column not in df.columns:
        return pd.Series()
    
    total = df[column].sum()
    return df[column] / total if total > 0 else 0


def create_performance_segments(df: pd.DataFrame, metric: str, 
                                segments: List[str] = None) -> pd.DataFrame:
    """
    Segment data into performance buckets
    
    Args:
        df: Input dataframe
        metric: Column to segment by
        segments: Custom segment names
    
    Returns:
        Dataframe with segment column
    """
    if df is None or df.empty or metric not in df.columns:
        return df
    
    result = df.copy()
    
    if segments is None:
        segments = ['Low', 'Medium', 'High', 'Elite']
    
    result[f'{metric}_segment'] = pd.qcut(
        result[metric], 
        q=len(segments), 
        labels=segments,
        duplicates='drop'
    )
    
    return result




def validate_numeric_range(value: float, min_val: float = None, 
                          max_val: float = None) -> bool:
    """
    Validate if a numeric value is within range
    
    Args:
        value: Value to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        True if valid, False otherwise
    """
    if pd.isna(value):
        return False
    
    if min_val is not None and value < min_val:
        return False
    
    if max_val is not None and value > max_val:
        return False
    
    return True


def detect_data_quality_issues(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect data quality issues in a dataframe
    
    Args:
        df: Input dataframe
    
    Returns:
        Dictionary with quality metrics
    """
    if df is None or df.empty:
        return {"empty": True}
    
    issues = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
    }
    
    # Check for negative values in spend/sales columns
    negative_checks = ['Spend', 'Sales', 'Clicks', 'Impressions', 'Orders']
    issues["negative_values"] = {}
    
    for col in negative_checks:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                issues["negative_values"][col] = int(negative_count)
    
    return issues




def parse_date_range(df: pd.DataFrame, date_column: str = 'Date') -> tuple:
    """
    Extract date range from dataframe
    
    Args:
        df: Input dataframe
        date_column: Name of date column
    
    Returns:
        Tuple of (start_date, end_date) as strings
    """
    if df is None or df.empty or date_column not in df.columns:
        return ("N/A", "N/A")
    
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        min_date = df[date_column].min()
        max_date = df[date_column].max()
        
        if pd.notna(min_date) and pd.notna(max_date):
            return (min_date.strftime('%Y-%m-%d'), max_date.strftime('%Y-%m-%d'))
    except Exception:
        pass
    
    return ("N/A", "N/A")


def get_week_over_week_change(current: float, previous: float) -> Dict[str, Any]:
    """
    Calculate week-over-week change
    
    Args:
        current: Current period value
        previous: Previous period value
    
    Returns:
        Dictionary with change metrics
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return {
            "change": 0,
            "change_pct": 0,
            "direction": "neutral"
        }
    
    change = current - previous
    change_pct = (change / previous) * 100
    
    return {
        "change": change,
        "change_pct": change_pct,
        "direction": "up" if change > 0 else "down" if change < 0 else "neutral"
    }




def clean_campaign_name(name: str) -> str:
    """Clean and standardize campaign names"""
    if pd.isna(name):
        return "Unknown"
    
    name = str(name).strip()
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name


def extract_match_type(text: str) -> str:
    """Extract match type from text"""
    if pd.isna(text):
        return "Unknown"
    
    text = str(text).lower()
    
    if 'exact' in text:
        return 'Exact'
    elif 'phrase' in text:
        return 'Phrase'
    elif 'broad' in text:
        return 'Broad'
    else:
        return 'Unknown'




def add_all_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all calculated metrics to dataframe
    Calculates ACOS, ROAS, CTR, CVR, CPC based on available columns
    
    Args:
        df: Input dataframe with raw metrics
    
    Returns:
        Dataframe with calculated metrics added
    """
    if df is None or df.empty:
        return df
    
    result = df.copy()
    
    # Calculate ACOS (Advertising Cost of Sale)
    if 'Spend' in result.columns and 'Sales' in result.columns:
        result['ACOS'] = result.apply(
            lambda row: calculate_acos(row['Spend'], row['Sales']), 
            axis=1
        )
    
    # Calculate ROAS (Return on Ad Spend)
    if 'Sales' in result.columns and 'Spend' in result.columns:
        result['ROAS'] = result.apply(
            lambda row: calculate_roas(row['Sales'], row['Spend']), 
            axis=1
        )
    
    # Calculate CTR (Click-Through Rate)
    if 'Clicks' in result.columns and 'Impressions' in result.columns:
        result['CTR'] = result.apply(
            lambda row: calculate_ctr(row['Clicks'], row['Impressions']), 
            axis=1
        )
    
    # Calculate CVR (Conversion Rate)
    if 'Orders' in result.columns and 'Clicks' in result.columns:
        result['CVR'] = result.apply(
            lambda row: calculate_cvr(row['Orders'], row['Clicks']), 
            axis=1
        )
    
    # Calculate CPC (Cost Per Click)
    if 'Spend' in result.columns and 'Clicks' in result.columns:
        result['CPC'] = result.apply(
            lambda row: calculate_cpc(row['Spend'], row['Clicks']), 
            axis=1
        )
    
    # Calculate CPM (Cost Per 1000 Impressions)
    if 'Spend' in result.columns and 'Impressions' in result.columns:
        result['CPM'] = result.apply(
            lambda row: calculate_cpm(row['Spend'], row['Impressions']), 
            axis=1
        )
    
    return result


def calculate_organic_cvr(units_ordered: float, sessions: float) -> float:
    """
    Calculate organic conversion rate for business reports
    
    Args:
        units_ordered: Number of units ordered
        sessions: Number of sessions
    
    Returns:
        Conversion rate as decimal
    """
    return safe_divide(units_ordered, sessions, 0.0)


def calculate_revenue_per_session(sales: float, sessions: float) -> float:
    """
    Calculate revenue per session
    
    Args:
        sales: Total sales
        sessions: Total sessions
    
    Returns:
        Revenue per session
    """
    return safe_divide(sales, sessions, 0.0)


def calculate_ntb_percentage(ntb_orders: float, total_orders: float) -> float:
    """
    Calculate New-to-Brand percentage
    
    Args:
        ntb_orders: New-to-brand orders
        total_orders: Total orders
    
    Returns:
        NTB percentage as decimal
    """
    return safe_divide(ntb_orders, total_orders, 0.0)


def calculate_wasted_spend(df: pd.DataFrame, sales_threshold: float = 0) -> float:
    """
    Calculate wasted spend (spend with no sales)
    
    Args:
        df: Dataframe with Spend and Sales columns
        sales_threshold: Sales threshold (default 0)
    
    Returns:
        Total wasted spend
    """
    if df is None or df.empty:
        return 0.0
    
    if 'Spend' not in df.columns or 'Sales' not in df.columns:
        return 0.0
    
    wasted = df[df['Sales'] <= sales_threshold]['Spend'].sum()
    return float(wasted)


def calculate_efficiency_metrics(df: pd.DataFrame) -> Dict[str, float]:
    if df is None or df.empty:
        return {}
    
    metrics = {}
    
    # totals
    if 'Spend' in df.columns:
        metrics['total_spend'] = df['Spend'].sum()
    
    if 'Sales' in df.columns:
        metrics['total_sales'] = df['Sales'].sum()
    
    if 'Clicks' in df.columns:
        metrics['total_clicks'] = df['Clicks'].sum()
    
    if 'Impressions' in df.columns:
        metrics['total_impressions'] = df['Impressions'].sum()
    
    if 'Orders' in df.columns:
        metrics['total_orders'] = df['Orders'].sum()
    
    # Calculated metrics
    if 'total_spend' in metrics and 'total_sales' in metrics:
        metrics['overall_acos'] = calculate_acos(metrics['total_spend'], metrics['total_sales'])
        metrics['overall_roas'] = calculate_roas(metrics['total_sales'], metrics['total_spend'])
    
    if 'total_clicks' in metrics and 'total_impressions' in metrics:
        metrics['overall_ctr'] = calculate_ctr(metrics['total_clicks'], metrics['total_impressions'])
    
    if 'total_orders' in metrics and 'total_clicks' in metrics:
        metrics['overall_cvr'] = calculate_cvr(metrics['total_orders'], metrics['total_clicks'])
    
    if 'total_spend' in metrics and 'total_clicks' in metrics:
        metrics['overall_cpc'] = calculate_cpc(metrics['total_spend'], metrics['total_clicks'])
    
    # Wasted spend
    if 'Spend' in df.columns and 'Sales' in df.columns:
        metrics['wasted_spend'] = calculate_wasted_spend(df)
        if 'total_spend' in metrics and metrics['total_spend'] > 0:
            metrics['wasted_spend_pct'] = metrics['wasted_spend'] / metrics['total_spend']
    
    return metrics


def aggregate_by_dimension(df: pd.DataFrame, dimension: str, 
                           metric_columns: List[str] = None) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    
    if dimension not in df.columns:
        return pd.DataFrame()
    
    if metric_columns is None:
        metric_columns = []
        possible_metrics = ['Spend', 'Sales', 'Clicks', 'Impressions', 'Orders', 
                          'Sessions', 'Units', 'Page Views', 'DPV']
        
        for col in possible_metrics:
            if col in df.columns:
                metric_columns.append(col)
    
    #aggregation
    agg_dict = {col: 'sum' for col in metric_columns if col in df.columns}
    
    if not agg_dict:
        return df[[dimension]].drop_duplicates()
    # Perform aggregation
    result = df.groupby(dimension, as_index=False).agg(agg_dict)
    
    # Add calculated metrics
    result = add_all_metrics(result)
    
    return result

def extract_date_range(df: pd.DataFrame, date_column: str = 'Start Date') -> Tuple[str, str]:

    if df is None or df.empty:
        return ("N/A", "N/A")
    
    possible_date_cols = [
        date_column,
        'Start Date',
        'End Date', 
        'Date',
        'Report Date',
        'Week',
        'Month'
    ]
    
    date_col = None
    for col in possible_date_cols:
        if col in df.columns:
            date_col = col
            break
    
    if date_col is None:
        return ("N/A", "N/A")
    
    try:
        # Convert to datetime
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
        
        # Drop NaT values
        df_copy = df_copy.dropna(subset=[date_col])
        
        if df_copy.empty:
            return ("N/A", "N/A")
        
        # -- min and max dates--
        min_date = df_copy[date_col].min()
        max_date = df_copy[date_col].max()
        
        if pd.notna(min_date) and pd.notna(max_date):
            return (
                min_date.strftime('%Y-%m-%d'),
                max_date.strftime('%Y-%m-%d')
            )
    
    except Exception as e:
        try:
            dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
            if not dates.empty:
                return (
                    dates.min().strftime('%Y-%m-%d'),
                    dates.max().strftime('%Y-%m-%d')
                )
        except:
            pass
    
    return ("N/A", "N/A")