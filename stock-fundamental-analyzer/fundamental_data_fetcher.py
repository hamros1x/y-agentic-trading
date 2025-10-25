"""
Stock Fundamental Data Fetcher - Consolidated Single File
Indian Stock Market (NSE/BSE) Analysis Tool
"""

import yfinance as yf
import pandas as pd
import logging
import sys
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

REPORTS_DIR = "fundamental_reports"
API_TIMEOUT = 10

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

# Configure logging
logging.basicConfig(
    filename='stock_analyzer.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class StockData:
    """Complete stock data container"""
    ticker: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Company info
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    headquarters: Optional[str] = None
    ceo: Optional[str] = None
    market_cap: Optional[float] = None
    
    # Valuation ratios
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_sales: Optional[float] = None
    enterprise_value: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    
    # Profitability
    roe: Optional[float] = None
    roa: Optional[float] = None
    net_margin: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    revenue_per_share: Optional[float] = None
    eps: Optional[float] = None
    
    # Financial health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    total_cash: Optional[float] = None
    total_debt: Optional[float] = None
    free_cash_flow: Optional[float] = None
    
    # Growth
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    quarterly_revenue_growth: Optional[float] = None
    quarterly_earnings_growth: Optional[float] = None
    
    # Price data
    current_price: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    previous_close: Optional[float] = None
    volume: Optional[float] = None
    avg_volume: Optional[float] = None
    beta: Optional[float] = None
    
    # Dividends
    dividend_rate: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    ex_dividend_date: Optional[datetime] = None
    five_year_avg_dividend_yield: Optional[float] = None
    
    # Financial statements
    income_statement: Optional[pd.DataFrame] = None
    balance_sheet: Optional[pd.DataFrame] = None
    cash_flow: Optional[pd.DataFrame] = None
    
    # Analyst data
    analyst_ratings: Optional[Dict] = None
    target_price_mean: Optional[float] = None
    target_price_high: Optional[float] = None
    target_price_low: Optional[float] = None
    num_analysts: Optional[int] = None


@dataclass
class InvestmentScore:
    """Container for investment score and breakdown"""
    total_score: float
    pe_score: float
    roe_score: float
    debt_score: float
    margin_score: float
    growth_score: float
    interpretation: str
    missing_metrics: List[str]


@dataclass
class FlagAnalysis:
    """Container for red and green flags"""
    red_flags: List[Tuple[str, str]]
    green_flags: List[Tuple[str, str]]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_large_number(value: float) -> str:
    """Format large numbers with Cr/L suffixes (Indian system)"""
    if value is None or (isinstance(value, float) and (value != value)):
        return "N/A"
    
    try:
        value = float(value)
        if value < 0:
            sign = "-"
            value = abs(value)
        else:
            sign = ""
        
        if value >= 1_00_00_000:  # 1 Crore or more
            return f"{sign}₹{value / 1_00_00_000:.2f} Cr"
        elif value >= 1_00_000:  # 1 Lakh or more
            return f"{sign}₹{value / 1_00_000:.2f} L"
        else:
            return f"{sign}₹{value:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text with ellipsis if too long"""
    if text is None:
        return "N/A"
    
    text = str(text)
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length - 3] + "..."


def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """Validate ticker format"""
    if not ticker or not isinstance(ticker, str):
        return False, "Ticker cannot be empty"
    
    ticker = ticker.strip().upper()
    pattern = r'^[A-Z0-9&]+\.(NS|BO)$'
    
    if re.match(pattern, ticker):
        return True, ""
    else:
        return False, "Invalid symbol format. Use: SYMBOL.NS for NSE or SYMBOL.BO for BSE"


def normalize_ticker(ticker: str) -> str:
    """Normalize ticker to uppercase and trim whitespace"""
    if not ticker:
        return ""
    return ticker.strip().upper()


def create_directory(path: str) -> None:
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)


def get_timestamp() -> str:
    """Get formatted timestamp string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def categorize_market_cap(market_cap: float) -> str:
    """Categorize market cap as Large/Mid/Small cap"""
    if market_cap is None:
        return "Unknown"
    
    if market_cap >= LARGE_CAP_MIN:
        return "Large Cap"
    elif market_cap >= MID_CAP_MIN:
        return "Mid Cap"
    else:
        return "Small Cap"

# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """Fetch all data for a single stock"""
    try:
        ticker_obj = yf.Ticker(ticker)
        stock_data = StockData(ticker=ticker)
        
        # Get info
        data = ticker_obj.info
        
        # Company info
        stock_data.company_name = data.get('longName') or data.get('shortName')
        stock_data.sector = data.get('sector')
        stock_data.industry = data.get('industry')
        stock_data.description = data.get('longBusinessSummary')
        stock_data.website = data.get('website')
        stock_data.employees = data.get('fullTimeEmployees')
        stock_data.headquarters = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
        stock_data.ceo = data.get('companyOfficers', [{}])[0].get('name') if data.get('companyOfficers') else None
        stock_data.market_cap = data.get('marketCap')
        
        # Valuation ratios
        stock_data.pe_ratio = data.get('trailingPE') or data.get('forwardPE')
        stock_data.pb_ratio = data.get('priceToBook')
        stock_data.peg_ratio = data.get('pegRatio')
        stock_data.price_to_sales = data.get('priceToSalesTrailing12Months')
        stock_data.enterprise_value = data.get('enterpriseValue')
        stock_data.ev_to_ebitda = data.get('enterpriseToEbitda')
        
        # Profitability metrics
        stock_data.roe = data.get('returnOnEquity')
        stock_data.roa = data.get('returnOnAssets')
        stock_data.net_margin = data.get('profitMargins')
        stock_data.gross_margin = data.get('grossMargins')
        stock_data.operating_margin = data.get('operatingMargins')
        stock_data.revenue_per_share = data.get('revenuePerShare')
        stock_data.eps = data.get('trailingEps')
        
        # Financial health
        stock_data.debt_to_equity = data.get('debtToEquity')
        stock_data.current_ratio = data.get('currentRatio')
        stock_data.quick_ratio = data.get('quickRatio')
        stock_data.total_cash = data.get('totalCash')
        stock_data.total_debt = data.get('totalDebt')
        stock_data.free_cash_flow = data.get('freeCashflow')
        
        # Growth metrics
        stock_data.revenue_growth = data.get('revenueGrowth')
        stock_data.earnings_growth = data.get('earningsGrowth')
        stock_data.quarterly_revenue_growth = data.get('revenueQuarterlyGrowth')
        stock_data.quarterly_earnings_growth = data.get('earningsQuarterlyGrowth')
        
        # Price data
        stock_data.current_price = data.get('currentPrice') or data.get('regularMarketPrice')
        stock_data.week_52_high = data.get('fiftyTwoWeekHigh')
        stock_data.week_52_low = data.get('fiftyTwoWeekLow')
        stock_data.day_high = data.get('dayHigh') or data.get('regularMarketDayHigh')
        stock_data.day_low = data.get('dayLow') or data.get('regularMarketDayLow')
        stock_data.previous_close = data.get('previousClose') or data.get('regularMarketPreviousClose')
        stock_data.volume = data.get('volume') or data.get('regularMarketVolume')
        stock_data.avg_volume = data.get('averageVolume')
        stock_data.beta = data.get('beta')
        
        # Dividend data
        stock_data.dividend_rate = data.get('dividendRate')
        stock_data.dividend_yield = data.get('dividendYield')
        stock_data.payout_ratio = data.get('payoutRatio')
        ex_div_date = data.get('exDividendDate')
        if ex_div_date:
            stock_data.ex_dividend_date = datetime.fromtimestamp(ex_div_date)
        stock_data.five_year_avg_dividend_yield = data.get('fiveYearAvgDividendYield')
        
        # Financial statements
        try:
            stock_data.income_statement = ticker_obj.financials
            stock_data.balance_sheet = ticker_obj.balance_sheet
            stock_data.cash_flow = ticker_obj.cashflow
        except:
            pass
        
        # Analyst data
        stock_data.target_price_mean = data.get('targetMeanPrice')
        stock_data.target_price_high = data.get('targetHighPrice')
        stock_data.target_price_low = data.get('targetLowPrice')
        stock_data.num_analysts = data.get('numberOfAnalystOpinions')
        
        # Check if we got any valid data
        if not stock_data.company_name and not stock_data.current_price:
            return None
        
        return stock_data
        
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker}: {str(e)}")
        return None

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_investment_score(data: StockData) -> InvestmentScore:
    """Calculate 0-100 investment quality score"""
    pe_score = 0
    roe_score = 0
    debt_score = 0
    margin_score = 0
    growth_score = 0
    missing_metrics = []
    
    # P/E Ratio Score (30 points max)
    if data.pe_ratio is not None and data.pe_ratio > 0:
        if data.pe_ratio < PE_EXCELLENT:
            pe_score = 30
        elif data.pe_ratio < PE_GOOD:
            pe_score = 20
        elif data.pe_ratio < PE_FAIR:
            pe_score = 10
        else:
            pe_score = 0
    else:
        missing_metrics.append('P/E Ratio')
    
    # ROE Score (20 points max)
    if data.roe is not None:
        roe_value = data.roe * 100 if data.roe < 1 else data.roe
        if roe_value > ROE_EXCELLENT:
            roe_score = 20
        elif roe_value > ROE_GOOD:
            roe_score = 15
        elif roe_value > ROE_FAIR:
            roe_score = 10
        elif roe_value > 5:
            roe_score = 5
        else:
            roe_score = 0
    else:
        missing_metrics.append('ROE')
    
    # Debt-to-Equity Score (20 points max)
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        if de_value < DEBT_EXCELLENT:
            debt_score = 20
        elif de_value < DEBT_GOOD:
            debt_score = 15
        elif de_value < DEBT_FAIR:
            debt_score = 10
        else:
            debt_score = 0
    else:
        missing_metrics.append('Debt-to-Equity')
    
    # Profit Margin Score (15 points max)
    if data.net_margin is not None:
        margin_value = data.net_margin * 100 if data.net_margin < 1 else data.net_margin
        if margin_value > MARGIN_EXCELLENT:
            margin_score = 15
        elif margin_value > MARGIN_GOOD:
            margin_score = 12
        elif margin_value > MARGIN_FAIR:
            margin_score = 8
        elif margin_value > 5:
            margin_score = 4
        else:
            margin_score = 0
    else:
        missing_metrics.append('Profit Margin')
    
    # Revenue Growth Score (15 points max)
    if data.revenue_growth is not None:
        growth_value = data.revenue_growth * 100 if abs(data.revenue_growth) < 1 else data.revenue_growth
        if growth_value > GROWTH_EXCELLENT:
            growth_score = 15
        elif growth_value > GROWTH_GOOD:
            growth_score = 12
        elif growth_value > GROWTH_FAIR:
            growth_score = 8
        elif growth_value > 0:
            growth_score = 4
        else:
            growth_score = 0
    else:
        missing_metrics.append('Revenue Growth')
    
    # Calculate total score
    total_score = pe_score + roe_score + debt_score + margin_score + growth_score
    
    # Generate interpretation
    if total_score >= 80:
        interpretation = "Excellent fundamentals"
    elif total_score >= 60:
        interpretation = "Good fundamentals"
    elif total_score >= 40:
        interpretation = "Average fundamentals"
    elif total_score >= 20:
        interpretation = "Weak fundamentals"
    else:
        interpretation = "Poor fundamentals"
    
    return InvestmentScore(
        total_score=total_score,
        pe_score=pe_score,
        roe_score=roe_score,
        debt_score=debt_score,
        margin_score=margin_score,
        growth_score=growth_score,
        interpretation=interpretation,
        missing_metrics=missing_metrics
    )


def identify_red_flags(data: StockData) -> List[Tuple[str, str]]:
    """Detect warning indicators"""
    red_flags = []
    
    # High debt
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        if de_value > RED_FLAG_DEBT:
            red_flags.append(("High Debt", f"Debt-to-Equity ratio of {de_value:.2f} indicates high leverage"))
    
    # Negative ROE
    if data.roe is not None:
        roe_value = data.roe * 100 if abs(data.roe) < 1 else data.roe
        if roe_value < 0:
            red_flags.append(("Negative ROE", f"Return on Equity of {roe_value:.2f}% indicates unprofitable operations"))
    
    # Declining revenue
    if data.revenue_growth is not None:
        growth_value = data.revenue_growth * 100 if abs(data.revenue_growth) < 1 else data.revenue_growth
        if growth_value < 0:
            red_flags.append(("Declining Revenue", f"Revenue declined by {abs(growth_value):.2f}% year-over-year"))
    
    # Negative profit margins
    if data.net_margin is not None:
        margin_value = data.net_margin * 100 if abs(data.net_margin) < 1 else data.net_margin
        if margin_value < 0:
            red_flags.append(("Negative Margins", f"Net profit margin of {margin_value:.2f}% indicates losses"))
    
    # High P/E
    if data.pe_ratio is not None and data.pe_ratio > RED_FLAG_PE:
        red_flags.append(("High P/E Ratio", f"P/E ratio of {data.pe_ratio:.2f} may indicate overvaluation"))
    
    # Negative cash flow
    if data.free_cash_flow is not None and data.free_cash_flow < 0:
        red_flags.append(("Negative Cash Flow", "Company is burning cash"))
    
    return red_flags


def identify_green_flags(data: StockData) -> List[Tuple[str, str]]:
    """Detect positive indicators"""
    green_flags = []
    
    # Strong ROE
    if data.roe is not None:
        roe_value = data.roe * 100 if abs(data.roe) < 1 else data.roe
        if roe_value > GREEN_FLAG_ROE:
            green_flags.append(("Strong ROE", f"Return on Equity of {roe_value:.2f}% shows efficient use of capital"))
    
    # Low debt
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        if de_value < GREEN_FLAG_DEBT:
            green_flags.append(("Low Debt", f"Debt-to-Equity ratio of {de_value:.2f} indicates strong balance sheet"))
    
    # Strong revenue growth
    if data.revenue_growth is not None:
        growth_value = data.revenue_growth * 100 if abs(data.revenue_growth) < 1 else data.revenue_growth
        if growth_value > GREEN_FLAG_GROWTH:
            green_flags.append(("Strong Growth", f"Revenue grew by {growth_value:.2f}% year-over-year"))
    
    # Healthy profit margins
    if data.net_margin is not None:
        margin_value = data.net_margin * 100 if abs(data.net_margin) < 1 else data.net_margin
        if margin_value > GREEN_FLAG_MARGIN:
            green_flags.append(("Healthy Margins", f"Net profit margin of {margin_value:.2f}% shows strong profitability"))
    
    # Positive free cash flow
    if data.free_cash_flow is not None and data.free_cash_flow > 0:
        green_flags.append(("Positive Cash Flow", "Company generates positive free cash flow"))
    
    # Reasonable P/E
    if data.pe_ratio is not None:
        if GREEN_FLAG_PE_MIN <= data.pe_ratio <= GREEN_FLAG_PE_MAX:
            green_flags.append(("Reasonable Valuation", f"P/E ratio of {data.pe_ratio:.2f} is in fair value range"))
    
    return green_flags

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def print_section_header(title: str) -> None:
    """Print formatted section header"""
    print(f"\n{'=' * 64}")
    print(f"{title.center(64)}")
    print(f"{'=' * 64}")


def print_metric(label: str, value: str) -> None:
    """Print formatted metric line"""
    print(f"{label}: {value}")


def display_company_overview(data: StockData) -> None:
    """Display formatted company information"""
    print_section_header("COMPANY INFORMATION")
    
    if data.company_name:
        print_metric("Company Name", data.company_name)
    
    if data.sector:
        print_metric("Sector", data.sector)
    
    if data.industry:
        print_metric("Industry", data.industry)
    
    if data.market_cap:
        category = categorize_market_cap(data.market_cap)
        print_metric("Market Cap", f"{format_large_number(data.market_cap)} ({category})")
    
    if data.employees:
        print_metric("Employees", f"{data.employees:,}")
    
    if data.headquarters:
        print_metric("Headquarters", data.headquarters)
    
    if data.website:
        print_metric("Website", data.website)
    
    if data.ceo:
        print_metric("CEO", data.ceo)
    
    if data.description:
        desc = truncate_text(data.description, 300)
        print(f"\nBusiness Description:")
        print(desc)


def display_valuation_ratios(data: StockData) -> None:
    """Display valuation metrics"""
    print_section_header("VALUATION RATIOS")
    
    print_metric("P/E Ratio", f"{data.pe_ratio:.2f}" if data.pe_ratio else "N/A")
    print_metric("P/B Ratio", f"{data.pb_ratio:.2f}" if data.pb_ratio else "N/A")
    print_metric("PEG Ratio", f"{data.peg_ratio:.2f}" if data.peg_ratio else "N/A")
    print_metric("Price to Sales", f"{data.price_to_sales:.2f}" if data.price_to_sales else "N/A")
    print_metric("Enterprise Value", format_large_number(data.enterprise_value) if data.enterprise_value else "N/A")
    print_metric("EV/EBITDA", f"{data.ev_to_ebitda:.2f}" if data.ev_to_ebitda else "N/A")


def display_profitability_metrics(data: StockData) -> None:
    """Display profitability indicators"""
    print_section_header("PROFITABILITY METRICS")
    
    if data.roe is not None:
        roe_pct = data.roe * 100 if abs(data.roe) < 1 else data.roe
        print_metric("ROE (Return on Equity)", f"{roe_pct:.2f}%")
    else:
        print_metric("ROE (Return on Equity)", "N/A")
    
    if data.roa is not None:
        roa_pct = data.roa * 100 if abs(data.roa) < 1 else data.roa
        print_metric("ROA (Return on Assets)", f"{roa_pct:.2f}%")
    else:
        print_metric("ROA (Return on Assets)", "N/A")
    
    if data.net_margin is not None:
        margin_pct = data.net_margin * 100 if abs(data.net_margin) < 1 else data.net_margin
        print_metric("Net Profit Margin", f"{margin_pct:.2f}%")
    else:
        print_metric("Net Profit Margin", "N/A")
    
    if data.gross_margin is not None:
        gross_pct = data.gross_margin * 100 if abs(data.gross_margin) < 1 else data.gross_margin
        print_metric("Gross Profit Margin", f"{gross_pct:.2f}%")
    else:
        print_metric("Gross Profit Margin", "N/A")
    
    if data.operating_margin is not None:
        op_pct = data.operating_margin * 100 if abs(data.operating_margin) < 1 else data.operating_margin
        print_metric("Operating Profit Margin", f"{op_pct:.2f}%")
    else:
        print_metric("Operating Profit Margin", "N/A")
    
    print_metric("EPS (Earnings Per Share)", f"₹{data.eps:.2f}" if data.eps else "N/A")
    print_metric("Revenue Per Share", f"₹{data.revenue_per_share:.2f}" if data.revenue_per_share else "N/A")


def display_financial_health(data: StockData) -> None:
    """Display debt, liquidity, and cash metrics"""
    print_section_header("FINANCIAL HEALTH")
    
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        print_metric("Debt-to-Equity Ratio", f"{de_value:.2f}")
    else:
        print_metric("Debt-to-Equity Ratio", "N/A")
    
    print_metric("Current Ratio", f"{data.current_ratio:.2f}" if data.current_ratio else "N/A")
    print_metric("Quick Ratio", f"{data.quick_ratio:.2f}" if data.quick_ratio else "N/A")
    print_metric("Total Cash", format_large_number(data.total_cash) if data.total_cash else "N/A")
    print_metric("Total Debt", format_large_number(data.total_debt) if data.total_debt else "N/A")
    print_metric("Free Cash Flow", format_large_number(data.free_cash_flow) if data.free_cash_flow else "N/A")


def display_growth_metrics(data: StockData) -> None:
    """Display growth rates"""
    print_section_header("GROWTH METRICS")
    
    if data.revenue_growth is not None:
        growth_pct = data.revenue_growth * 100 if abs(data.revenue_growth) < 1 else data.revenue_growth
        print_metric("Revenue Growth (YoY)", f"{growth_pct:.2f}%")
    else:
        print_metric("Revenue Growth (YoY)", "N/A")
    
    if data.earnings_growth is not None:
        earn_pct = data.earnings_growth * 100 if abs(data.earnings_growth) < 1 else data.earnings_growth
        print_metric("Earnings Growth (YoY)", f"{earn_pct:.2f}%")
    else:
        print_metric("Earnings Growth (YoY)", "N/A")
    
    if data.quarterly_revenue_growth is not None:
        qrev_pct = data.quarterly_revenue_growth * 100 if abs(data.quarterly_revenue_growth) < 1 else data.quarterly_revenue_growth
        print_metric("Quarterly Revenue Growth", f"{qrev_pct:.2f}%")
    else:
        print_metric("Quarterly Revenue Growth", "N/A")
    
    if data.quarterly_earnings_growth is not None:
        qearn_pct = data.quarterly_earnings_growth * 100 if abs(data.quarterly_earnings_growth) < 1 else data.quarterly_earnings_growth
        print_metric("Quarterly Earnings Growth", f"{qearn_pct:.2f}%")
    else:
        print_metric("Quarterly Earnings Growth", "N/A")


def display_price_analysis(data: StockData) -> None:
    """Display current price and trading statistics"""
    print_section_header("STOCK PRICE ANALYSIS")
    
    print_metric("Current Price", f"₹{data.current_price:.2f}" if data.current_price else "N/A")
    print_metric("Previous Close", f"₹{data.previous_close:.2f}" if data.previous_close else "N/A")
    
    if data.day_high and data.day_low:
        print_metric("Day's Range", f"₹{data.day_low:.2f} - ₹{data.day_high:.2f}")
    else:
        print_metric("Day's Range", "N/A")
    
    if data.week_52_high:
        print_metric("52-Week High", f"₹{data.week_52_high:.2f}")
        if data.current_price:
            pct_from_high = ((data.current_price - data.week_52_high) / data.week_52_high) * 100
            print(f"  ({pct_from_high:+.2f}% from 52-week high)")
    else:
        print_metric("52-Week High", "N/A")
    
    if data.week_52_low:
        print_metric("52-Week Low", f"₹{data.week_52_low:.2f}")
        if data.current_price:
            pct_from_low = ((data.current_price - data.week_52_low) / data.week_52_low) * 100
            print(f"  ({pct_from_low:+.2f}% from 52-week low)")
    else:
        print_metric("52-Week Low", "N/A")
    
    print_metric("Volume", f"{int(data.volume):,}" if data.volume else "N/A")
    print_metric("Average Volume", f"{int(data.avg_volume):,}" if data.avg_volume else "N/A")
    print_metric("Beta (Volatility)", f"{data.beta:.2f}" if data.beta else "N/A")


def display_dividend_info(data: StockData) -> None:
    """Display dividend information"""
    print_section_header("DIVIDEND INFORMATION")
    
    has_dividend = any([data.dividend_rate, data.dividend_yield, data.payout_ratio])
    
    if not has_dividend:
        print("No dividend information available for this stock")
        return
    
    print_metric("Dividend Rate (Annual)", f"₹{data.dividend_rate:.2f}" if data.dividend_rate else "N/A")
    
    if data.dividend_yield:
        yield_pct = data.dividend_yield * 100 if data.dividend_yield < 1 else data.dividend_yield
        print_metric("Dividend Yield", f"{yield_pct:.2f}%")
    else:
        print_metric("Dividend Yield", "N/A")
    
    if data.payout_ratio:
        payout_pct = data.payout_ratio * 100 if data.payout_ratio < 1 else data.payout_ratio
        print_metric("Payout Ratio", f"{payout_pct:.2f}%")
    else:
        print_metric("Payout Ratio", "N/A")
    
    if data.ex_dividend_date:
        print_metric("Ex-Dividend Date", data.ex_dividend_date.strftime("%Y-%m-%d"))
    else:
        print_metric("Ex-Dividend Date", "N/A")
    
    if data.five_year_avg_dividend_yield:
        avg_yield_pct = data.five_year_avg_dividend_yield * 100 if data.five_year_avg_dividend_yield < 1 else data.five_year_avg_dividend_yield
        print_metric("5-Year Avg Dividend Yield", f"{avg_yield_pct:.2f}%")
    else:
        print_metric("5-Year Avg Dividend Yield", "N/A")


def display_analyst_recommendations(data: StockData) -> None:
    """Display analyst ratings and target prices"""
    print_section_header("ANALYST RECOMMENDATIONS")
    
    has_analyst_data = any([data.target_price_mean, data.target_price_high, data.target_price_low, data.num_analysts])
    
    if not has_analyst_data:
        print("Analyst recommendations not available for this stock")
        return
    
    print_metric("Number of Analysts", str(data.num_analysts) if data.num_analysts else "N/A")
    print_metric("Target Price (Mean)", f"₹{data.target_price_mean:.2f}" if data.target_price_mean else "N/A")
    print_metric("Target Price (High)", f"₹{data.target_price_high:.2f}" if data.target_price_high else "N/A")
    print_metric("Target Price (Low)", f"₹{data.target_price_low:.2f}" if data.target_price_low else "N/A")
    
    if data.target_price_mean and data.current_price:
        potential = ((data.target_price_mean - data.current_price) / data.current_price) * 100
        print(f"\nPotential: {potential:+.2f}% from current price")


def display_investment_score(score: InvestmentScore) -> None:
    """Display score with interpretation"""
    print_section_header("INVESTMENT QUALITY SCORE")
    
    print(f"\nTotal Score: {score.total_score:.0f}/100 - {score.interpretation}")
    print(f"\nScore Breakdown:")
    print(f"  P/E Ratio Score:      {score.pe_score:.0f}/30")
    print(f"  ROE Score:            {score.roe_score:.0f}/20")
    print(f"  Debt-to-Equity Score: {score.debt_score:.0f}/20")
    print(f"  Profit Margin Score:  {score.margin_score:.0f}/15")
    print(f"  Revenue Growth Score: {score.growth_score:.0f}/15")
    
    if score.missing_metrics:
        print(f"\nNote: Score calculated without: {', '.join(score.missing_metrics)}")


def display_flags(flags: FlagAnalysis) -> None:
    """Display red and green flags"""
    print_section_header("RED FLAGS (Warning Signs)")
    
    if flags.red_flags:
        for flag_name, description in flags.red_flags:
            print(f"\n[X] {flag_name}")
            print(f"    {description}")
    else:
        print("\n[OK] No major red flags detected")
    
    print_section_header("GREEN FLAGS (Positive Signs)")
    
    if flags.green_flags:
        for flag_name, description in flags.green_flags:
            print(f"\n[+] {flag_name}")
            print(f"    {description}")
    else:
        print("\nNo significant green flags detected")

# ============================================================================
# REPORT BUILDING
# ============================================================================

def build_report(stock_data: StockData, score: InvestmentScore, flags: FlagAnalysis) -> str:
    """Build complete text report with all sections"""
    lines = []
    lines.append("=" * 70)
    lines.append("FUNDAMENTAL ANALYSIS - " + stock_data.ticker)
    lines.append("=" * 70)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    
    # Company Overview
    lines.append("COMPANY INFORMATION")
    lines.append("-" * 70)
    if stock_data.company_name:
        lines.append(f"Company Name: {stock_data.company_name}")
    if stock_data.sector:
        lines.append(f"Sector: {stock_data.sector}")
    if stock_data.industry:
        lines.append(f"Industry: {stock_data.industry}")
    if stock_data.market_cap:
        category = categorize_market_cap(stock_data.market_cap)
        lines.append(f"Market Cap: {format_large_number(stock_data.market_cap)} ({category})")
    if stock_data.employees:
        lines.append(f"Employees: {stock_data.employees:,}")
    if stock_data.headquarters:
        lines.append(f"Headquarters: {stock_data.headquarters}")
    if stock_data.website:
        lines.append(f"Website: {stock_data.website}")
    if stock_data.ceo:
        lines.append(f"CEO: {stock_data.ceo}")
    if stock_data.description:
        lines.append(f"\nBusiness: {truncate_text(stock_data.description, 300)}")
    lines.append("")
    
    # Investment Score
    lines.append("INVESTMENT QUALITY SCORE")
    lines.append("-" * 70)
    lines.append(f"Total Score: {score.total_score:.0f}/100 - {score.interpretation}")
    lines.append(f"  P/E Ratio Score: {score.pe_score:.0f}/30")
    lines.append(f"  ROE Score: {score.roe_score:.0f}/20")
    lines.append(f"  Debt-to-Equity Score: {score.debt_score:.0f}/20")
    lines.append(f"  Profit Margin Score: {score.margin_score:.0f}/15")
    lines.append(f"  Revenue Growth Score: {score.growth_score:.0f}/15")
    if score.missing_metrics:
        lines.append(f"\nNote: Score calculated without: {', '.join(score.missing_metrics)}")
    lines.append("")
    
    # Red Flags
    lines.append("RED FLAGS")
    lines.append("-" * 70)
    if flags.red_flags:
        for flag_name, description in flags.red_flags:
            lines.append(f"[X] {flag_name}: {description}")
    else:
        lines.append("[OK] No major red flags detected")
    lines.append("")
    
    # Green Flags
    lines.append("GREEN FLAGS")
    lines.append("-" * 70)
    if flags.green_flags:
        for flag_name, description in flags.green_flags:
            lines.append(f"[+] {flag_name}: {description}")
    else:
        lines.append("No significant green flags detected")
    lines.append("")
    
    # Valuation Ratios
    lines.append("VALUATION RATIOS")
    lines.append("-" * 70)
    if stock_data.pe_ratio:
        lines.append(f"P/E Ratio: {stock_data.pe_ratio:.2f}")
    if stock_data.pb_ratio:
        lines.append(f"P/B Ratio: {stock_data.pb_ratio:.2f}")
    if stock_data.peg_ratio:
        lines.append(f"PEG Ratio: {stock_data.peg_ratio:.2f}")
    if stock_data.price_to_sales:
        lines.append(f"Price to Sales: {stock_data.price_to_sales:.2f}")
    if stock_data.enterprise_value:
        lines.append(f"Enterprise Value: {format_large_number(stock_data.enterprise_value)}")
    if stock_data.ev_to_ebitda:
        lines.append(f"EV/EBITDA: {stock_data.ev_to_ebitda:.2f}")
    lines.append("")
    
    # Profitability
    lines.append("PROFITABILITY METRICS")
    lines.append("-" * 70)
    if stock_data.roe:
        roe_pct = stock_data.roe * 100 if abs(stock_data.roe) < 1 else stock_data.roe
        lines.append(f"ROE: {roe_pct:.2f}%")
    if stock_data.roa:
        roa_pct = stock_data.roa * 100 if abs(stock_data.roa) < 1 else stock_data.roa
        lines.append(f"ROA: {roa_pct:.2f}%")
    if stock_data.net_margin:
        margin_pct = stock_data.net_margin * 100 if abs(stock_data.net_margin) < 1 else stock_data.net_margin
        lines.append(f"Net Profit Margin: {margin_pct:.2f}%")
    if stock_data.gross_margin:
        gross_pct = stock_data.gross_margin * 100 if abs(stock_data.gross_margin) < 1 else stock_data.gross_margin
        lines.append(f"Gross Profit Margin: {gross_pct:.2f}%")
    if stock_data.operating_margin:
        op_pct = stock_data.operating_margin * 100 if abs(stock_data.operating_margin) < 1 else stock_data.operating_margin
        lines.append(f"Operating Profit Margin: {op_pct:.2f}%")
    if stock_data.eps:
        lines.append(f"EPS: ₹{stock_data.eps:.2f}")
    if stock_data.revenue_per_share:
        lines.append(f"Revenue Per Share: ₹{stock_data.revenue_per_share:.2f}")
    lines.append("")
    
    # Financial Health
    lines.append("FINANCIAL HEALTH")
    lines.append("-" * 70)
    if stock_data.debt_to_equity:
        de_value = stock_data.debt_to_equity / 100 if stock_data.debt_to_equity > 10 else stock_data.debt_to_equity
        lines.append(f"Debt-to-Equity: {de_value:.2f}")
    if stock_data.current_ratio:
        lines.append(f"Current Ratio: {stock_data.current_ratio:.2f}")
    if stock_data.quick_ratio:
        lines.append(f"Quick Ratio: {stock_data.quick_ratio:.2f}")
    if stock_data.total_cash:
        lines.append(f"Total Cash: {format_large_number(stock_data.total_cash)}")
    if stock_data.total_debt:
        lines.append(f"Total Debt: {format_large_number(stock_data.total_debt)}")
    if stock_data.free_cash_flow:
        lines.append(f"Free Cash Flow: {format_large_number(stock_data.free_cash_flow)}")
    lines.append("")
    
    # Growth
    lines.append("GROWTH METRICS")
    lines.append("-" * 70)
    if stock_data.revenue_growth:
        growth_pct = stock_data.revenue_growth * 100 if abs(stock_data.revenue_growth) < 1 else stock_data.revenue_growth
        lines.append(f"Revenue Growth (YoY): {growth_pct:.2f}%")
    if stock_data.earnings_growth:
        earn_pct = stock_data.earnings_growth * 100 if abs(stock_data.earnings_growth) < 1 else stock_data.earnings_growth
        lines.append(f"Earnings Growth (YoY): {earn_pct:.2f}%")
    if stock_data.quarterly_revenue_growth:
        qrev_pct = stock_data.quarterly_revenue_growth * 100 if abs(stock_data.quarterly_revenue_growth) < 1 else stock_data.quarterly_revenue_growth
        lines.append(f"Quarterly Revenue Growth: {qrev_pct:.2f}%")
    if stock_data.quarterly_earnings_growth:
        qearn_pct = stock_data.quarterly_earnings_growth * 100 if abs(stock_data.quarterly_earnings_growth) < 1 else stock_data.quarterly_earnings_growth
        lines.append(f"Quarterly Earnings Growth: {qearn_pct:.2f}%")
    lines.append("")
    
    # Price Analysis
    lines.append("STOCK PRICE ANALYSIS")
    lines.append("-" * 70)
    if stock_data.current_price:
        lines.append(f"Current Price: ₹{stock_data.current_price:.2f}")
    if stock_data.previous_close:
        lines.append(f"Previous Close: ₹{stock_data.previous_close:.2f}")
    if stock_data.day_high and stock_data.day_low:
        lines.append(f"Day's Range: ₹{stock_data.day_low:.2f} - ₹{stock_data.day_high:.2f}")
    if stock_data.week_52_high:
        lines.append(f"52-Week High: ₹{stock_data.week_52_high:.2f}")
    if stock_data.week_52_low:
        lines.append(f"52-Week Low: ₹{stock_data.week_52_low:.2f}")
    if stock_data.volume:
        lines.append(f"Volume: {int(stock_data.volume):,}")
    if stock_data.avg_volume:
        lines.append(f"Average Volume: {int(stock_data.avg_volume):,}")
    if stock_data.beta:
        lines.append(f"Beta: {stock_data.beta:.2f}")
    lines.append("")
    
    # Dividends
    if any([stock_data.dividend_rate, stock_data.dividend_yield, stock_data.payout_ratio]):
        lines.append("DIVIDEND INFORMATION")
        lines.append("-" * 70)
        if stock_data.dividend_rate:
            lines.append(f"Dividend Rate (Annual): ₹{stock_data.dividend_rate:.2f}")
        if stock_data.dividend_yield:
            yield_pct = stock_data.dividend_yield * 100 if stock_data.dividend_yield < 1 else stock_data.dividend_yield
            lines.append(f"Dividend Yield: {yield_pct:.2f}%")
        if stock_data.payout_ratio:
            payout_pct = stock_data.payout_ratio * 100 if stock_data.payout_ratio < 1 else stock_data.payout_ratio
            lines.append(f"Payout Ratio: {payout_pct:.2f}%")
        if stock_data.ex_dividend_date:
            lines.append(f"Ex-Dividend Date: {stock_data.ex_dividend_date.strftime('%Y-%m-%d')}")
        if stock_data.five_year_avg_dividend_yield:
            avg_yield_pct = stock_data.five_year_avg_dividend_yield * 100 if stock_data.five_year_avg_dividend_yield < 1 else stock_data.five_year_avg_dividend_yield
            lines.append(f"5-Year Avg Dividend Yield: {avg_yield_pct:.2f}%")
        lines.append("")
    
    # Analyst Recommendations
    if any([stock_data.target_price_mean, stock_data.target_price_high, stock_data.target_price_low, stock_data.num_analysts]):
        lines.append("ANALYST RECOMMENDATIONS")
        lines.append("-" * 70)
        if stock_data.num_analysts:
            lines.append(f"Number of Analysts: {stock_data.num_analysts}")
        if stock_data.target_price_mean:
            lines.append(f"Target Price (Mean): ₹{stock_data.target_price_mean:.2f}")
        if stock_data.target_price_high:
            lines.append(f"Target Price (High): ₹{stock_data.target_price_high:.2f}")
        if stock_data.target_price_low:
            lines.append(f"Target Price (Low): ₹{stock_data.target_price_low:.2f}")
        if stock_data.target_price_mean and stock_data.current_price:
            potential = ((stock_data.target_price_mean - stock_data.current_price) / stock_data.current_price) * 100
            lines.append(f"Potential: {potential:+.2f}% from current price")
        lines.append("")
    
    # Disclaimer
    lines.append("=" * 70)
    lines.append("DISCLAIMER")
    lines.append("-" * 70)
    lines.append("This report is for informational purposes only and should not be")
    lines.append("considered as investment advice. Please consult with a financial")
    lines.append("advisor before making investment decisions.")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def save_report(content: str, ticker: str) -> str:
    """Save report to file and return file path"""
    create_directory(REPORTS_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ticker}_fundamental_{timestamp}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        raise IOError(f"Failed to save report: {str(e)}")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def analyze_stock(ticker: str) -> None:
    """Analyze a single stock and display results"""
    print(f"\nFetching fundamental data for {ticker}...")
    
    try:
        stock_data = fetch_stock_data(ticker)
        
        if stock_data is None:
            print(f"\nUnable to fetch data for {ticker}.")
            print("\nSuggestions:")
            print("• Check if the stock symbol is correct (e.g., RELIANCE.NS for NSE)")
            print("• Verify the stock is listed on NSE (.NS) or BSE (.BO)")
            print("• Ensure your internet connection is active")
            print("• Try again in a few moments if the service is busy")
            return
        
        print("Data retrieved successfully\n")
        
        # Display all sections
        display_company_overview(stock_data)
        display_valuation_ratios(stock_data)
        display_profitability_metrics(stock_data)
        display_financial_health(stock_data)
        display_growth_metrics(stock_data)
        display_price_analysis(stock_data)
        display_dividend_info(stock_data)
        display_analyst_recommendations(stock_data)
        
        # Calculate and display score
        score = calculate_investment_score(stock_data)
        display_investment_score(score)
        
        # Identify and display flags
        red_flags = identify_red_flags(stock_data)
        green_flags = identify_green_flags(stock_data)
        flags = FlagAnalysis(red_flags=red_flags, green_flags=green_flags)
        display_flags(flags)
        
        # Build report content (same as terminal output)
        report_content = build_report(stock_data, score, flags)
        
        # Save report automatically
        try:
            filepath = save_report(report_content, ticker)
            print(f"\n{'=' * 64}")
            print(f"Report saved: {filepath}")
            print(f"{'=' * 64}")
        except Exception as e:
            print(f"\nFailed to save report: {str(e)}")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please try again or contact support if the issue persists.")


def main():
    """Application entry point"""
    print("=" * 64)
    print("STOCK FUNDAMENTAL DATA FETCHER".center(64))
    print("Indian Stock Market (NSE/BSE) Analysis Tool".center(64))
    print("=" * 64)
    
    while True:
        print()
        ticker_input = input("Enter stock symbol (e.g., RELIANCE.NS, TCS.NS): ").strip()
        
        if not ticker_input:
            print("Stock symbol cannot be empty. Please try again.")
            continue
        
        # Validate ticker
        is_valid, error_msg = validate_ticker(ticker_input)
        if not is_valid:
            print(f"\nError: {error_msg}")
            continue
        
        ticker = normalize_ticker(ticker_input)
        
        # Analyze the stock
        analyze_stock(ticker)
        
        # Ask if user wants to analyze another stock
        print()
        another = input("Analyze another stock? (y/n): ").strip().lower()
        if another != 'y':
            print("\nThank you for using Stock Fundamental Data Fetcher!")
            print("Happy Investing!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)
