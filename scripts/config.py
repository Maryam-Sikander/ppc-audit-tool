class Theme:
    COLORS = {
        'primary': '#0f172a',  
        'secondary': '#475569', 
        'success': '#059669',  
        'warning': '#d97706',   
        'danger': '#dc2626',    
        'info': '#2563eb',    
        'background': '#f8fafc',
        'card': '#ffffff',     
        'text': '#1e293b',      
        'text_secondary': '#64748b' 
    }
    
    CHART_COLORS = [
        '#0f172a', '#2563eb', '#059669', 
        '#d97706', '#dc2626', '#475569',
        '#0284c7', '#4f46e5', '#be185d'
    ]
    
    GRADIENT_PRIMARY = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #059669 0%, #047857 100%)"
    GRADIENT_DANGER = "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)"


class ColumnMappings:
    
    # SP/SB Search Term Reports
    SEARCH_TERM_COLUMNS = {
        'clicks': ['Clicks'],
        'impressions': ['Impressions'],
        'spend': ['Spend', 'Total Spend'],
        'sales': ['7 Day Total Sales', '7 Day Total Sales ', '14 Day Total Sales', '14 Day Total Sales '],
        'orders': ['7 Day Total Orders (#)', '14 Day Total Orders (#)', 'Total Orders', 'Orders'],
        'units': ['7 Day Total Units (#)', '14 Day Total Units (#)', 'Total Units', 'Units', 'units'],
        'match_type': ['Match Type'],
        'start_date': ['Start Date'],
        'end_date': ['End Date']
    }
    
    # Placement Reports
    PLACEMENT_COLUMNS = {
        'clicks': ['Clicks'],
        'impressions': ['Impressions'],
        'spend': ['Spend', 'Total Spend'],
        'sales': ['7 Day Total Sales', '7 Day Total Sales ', '14 Day Total Sales', '14 Day Total Sales '],
        'orders': ['7 Day Total Orders (#)', '14 Day Total Orders (#)', 'Total Orders', 'Orders'],
        'placement': ['Placement'],
        'start_date': ['Start Date'],
        'end_date': ['End Date']
    }
    
    # Sponsored Display
    SD_COLUMNS = {
        'start_date': ['Start Date'],
        'end_date': ['End Date'],
        'campaign': ['Campaign Name'],
        'ad_group': ['Ad Group Name'],
        'targeting': ['Targeting'],
        'impressions': ['Impressions'],
        'viewable_impressions': ['Viewable Impressions'],
        'clicks': ['Clicks'],
        'units': ['14 Day Total Units (#)'],
        'ctr': ['Click-Thru Rate (CTR)'],
        'dpv': ['14 Day Detail Page Views (DPV)'],
        'cpc': ['Cost Per Click (CPC)'],
        'vcpm': ['Cost per 1,000 viewable impressions (VCPM)'],
        'spend': ['Spend'],
        'wasted_clicks': ['wasted clicks'],
        'wasted_spend': ['Wasted Spend'],
        'acos': ['Total Advertising Cost of Sales (ACOS)'],
        'roas': ['Total Return on Advertising Spend (ROAS)'],
        'orders': ['14 Day Total Orders (#)'],
        'sales': ['14 Day Total Sales'],
        'ntb_orders': ['14 Day New-to-brand Orders (#)'],
        'ntb_sales': ['14 Day New-to-brand Sales'],
        'ntb_units': ['14 Day New-to-brand Units (#)']
    }
    
    # Business Report (Organic)
    BUSINESS_COLUMNS = {
        'parent_asin': ['(Parent) ASIN'],
        'child_asin': ['(Child) ASIN'],
        'title': ['Title'],
        'sessions': ['Sessions - Total'],
        'sessions_b2b': ['Sessions - Total - B2B'],
        'page_views': ['Page Views - Total'],
        'page_views_b2b': ['Page Views - Total - B2B'],
        'buy_box': ['Featured Offer (Buy Box) Percentage'],
        'buy_box_b2b': ['Featured Offer (Buy Box) Percentage - B2B'],
        'units_ordered': ['Units Ordered'],
        'units_ordered_b2b': ['Units Ordered - B2B'],
        'unit_session_pct': ['Unit Session Percentage'],
        'ordered_sales': ['Ordered Product Sales'],
        'ordered_sales_b2b': ['Ordered Product Sales - B2B'],
        'order_items': ['Total Order Items'],
        'order_items_b2b': ['Total Order Items - B2B']
    }
    
    # SQP Reports
    SQP_COLUMNS = {
        'search_query': ['Search Query'],
        'query_score': ['Search Query Score'],
        'query_volume': ['Search Query Volume'],
        'impressions_total': ['Impressions: Total Count'],
        'impressions_brand': ['Impressions: Brand Count'],
        'impressions_share': ['Impressions: Brand Share %'],
        'clicks_total': ['Clicks: Total Count'],
        'clicks_rate': ['Clicks: Click Rate %'],
        'clicks_brand': ['Clicks: Brand Count'],
        'clicks_share': ['Clicks: Brand Share %'],
        'clicks_price': ['Clicks: Price (Median)'],
        'clicks_brand_price': ['Clicks: Brand Price (Median)'],
        'cart_total': ['Cart Adds: Total Count'],
        'cart_rate': ['Cart Adds: Cart Add Rate %'],
        'cart_brand': ['Cart Adds: Brand Count'],
        'cart_share': ['Cart Adds: Brand Share %'],
        'purchases_total': ['Purchases: Total Count'],
        'purchases_rate': ['Purchases: Purchase Rate %'],
        'purchases_brand': ['Purchases: Brand Count'],
        'purchases_share': ['Purchases: Brand Share %'],
        'purchases_price': ['Purchases: Price (Median)'],
        'purchases_brand_price': ['Purchases: Brand Price (Median)'],
        'reporting_date': ['Reporting Date']
    }


class Metrics:
    
    BASIC_METRICS = ['Clicks', 'Impressions', 'Spend', 'Sales', 'Orders']
    
    CALCULATED_METRICS = {
        'CPC': 'Cost Per Click',
        'CTR': 'Click Through Rate',
        'CVR': 'Conversion Rate',
        'ACOS': 'Advertising Cost of Sales',
        'ROAS': 'Return on Ad Spend',
        'CAC': 'Cost per Acquisition'
    }
    
    SD_SPECIFIC = ['VCPM', 'DPV', 'Wasted Spend %', 'NTB %']
    
    ORGANIC_METRICS = ['Sessions', 'Page Views', 'Buy Box %', 'Organic CVR']
    
    SQP_METRICS = ['Brand Share', 'Opportunity Score', 'Price Gap']


class Benchmarks:    
    GOOD_ACOS = 0.30  # 30%
    GOOD_ROAS = 3.0
    GOOD_CTR = 0.005  # 0.5%
    GOOD_CVR = 0.10   # 10%
    
    # Sponsored Display
    WASTED_SPEND_THRESHOLD = 0.20  
    NTB_TARGET = 0.15  # 15% 
    
    # Organic performance
    GOOD_BUY_BOX = 0.80  
    GOOD_ORGANIC_CVR = 0.12 
    
    # SQP Analysis
    LOW_BRAND_SHARE = 0.10  
    HIGH_BRAND_SHARE = 0.30  


class ReportTypes:
    SP_SEARCH = "sp_search"
    SP_PLACEMENT = "sp_placement"
    SB_SEARCH = "sb_search"
    SB_PLACEMENT = "sb_placement"
    SD_TARGETING = "sd_targeting"
    BUSINESS = "business"
    SQP = "sqp"


class Quarters:
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"
    
    ALL = [Q1, Q2, Q3, Q4]
    
    MONTH_MAPPING = {
        1: Q1, 2: Q1, 3: Q1,
        4: Q2, 5: Q2, 6: Q2,
        7: Q3, 8: Q3, 9: Q3,
        10: Q4, 11: Q4, 12: Q4
    }