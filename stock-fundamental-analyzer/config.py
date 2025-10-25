"""
Configuration constants and settings for Stock Fundamental Analyzer
"""

# Directories
REPORTS_DIR = "fundamental_reports"
CHARTS_DIR = "charts"

# Data fetching
API_TIMEOUT = 10  # seconds
DATA_FRESHNESS_HOURS = 24

# Scoring thresholds
PE_EXCELLENT = 15
PE_GOOD = 25
PE_FAIR = 35

ROE_EXCELLENT = 20
ROE_GOOD = 15
ROE_FAIR = 10

DEBT_EXCELLENT = 0.5
DEBT_GOOD = 1.0
DEBT_FAIR = 2.0

MARGIN_EXCELLENT = 20
MARGIN_GOOD = 15
MARGIN_FAIR = 10

GROWTH_EXCELLENT = 20
GROWTH_GOOD = 10
GROWTH_FAIR = 5

# Flag thresholds
RED_FLAG_DEBT = 2.0
RED_FLAG_PE = 50
GREEN_FLAG_ROE = 15
GREEN_FLAG_MARGIN = 15
GREEN_FLAG_GROWTH = 10
GREEN_FLAG_DEBT = 0.5
GREEN_FLAG_PE_MIN = 10
GREEN_FLAG_PE_MAX = 25

# Market cap categories (in INR)
LARGE_CAP_MIN = 20000_00_00_000  # 20,000 Cr
MID_CAP_MIN = 5000_00_00_000     # 5,000 Cr

# Display settings
MAX_PEERS = 5
TABLE_MAX_WIDTH = 120
DECIMAL_PLACES = 2

# Chart settings
CHART_FIGSIZE = (10, 6)
CHART_DPI = 100
CHART_STYLE = 'seaborn-v0_8-darkgrid'

# Popular stock symbols
POPULAR_STOCKS = {
    'Large Cap': [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'BHARTIARTL.NS', 'SBIN.NS',
        'BAJFINANCE.NS', 'ASIANPAINT.NS'
    ],
    'Mid Cap': [
        'ZOMATO.NS', 'NYKAA.NS', 'DMART.NS'
    ]
}
