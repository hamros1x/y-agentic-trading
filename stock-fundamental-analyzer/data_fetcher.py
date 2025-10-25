"""
Data Fetcher Module
Handles all yfinance data retrieval operations
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd


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
    market_cap_category: Optional[str] = None
    
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
    
    # Peer data
    peer_tickers: Optional[List[str]] = None



import yfinance as yf
import logging
from config import API_TIMEOUT


def fetch_company_info(ticker_obj: yf.Ticker) -> Dict:
    """Extract company overview information"""
    info = {}
    try:
        data = ticker_obj.info
        info['company_name'] = data.get('longName') or data.get('shortName')
        info['sector'] = data.get('sector')
        info['industry'] = data.get('industry')
        info['description'] = data.get('longBusinessSummary')
        info['website'] = data.get('website')
        info['employees'] = data.get('fullTimeEmployees')
        info['headquarters'] = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
        info['ceo'] = data.get('companyOfficers', [{}])[0].get('name') if data.get('companyOfficers') else None
        info['market_cap'] = data.get('marketCap')
    except Exception as e:
        logging.error(f"Error fetching company info: {str(e)}")
    return info


def fetch_financial_ratios(ticker_obj: yf.Ticker) -> Dict:
    """Extract valuation and profitability ratios"""
    ratios = {}
    try:
        data = ticker_obj.info
        # Valuation ratios
        ratios['pe_ratio'] = data.get('trailingPE') or data.get('forwardPE')
        ratios['pb_ratio'] = data.get('priceToBook')
        ratios['peg_ratio'] = data.get('pegRatio')
        ratios['price_to_sales'] = data.get('priceToSalesTrailing12Months')
        ratios['enterprise_value'] = data.get('enterpriseValue')
        ratios['ev_to_ebitda'] = data.get('enterpriseToEbitda')
        
        # Profitability metrics
        ratios['roe'] = data.get('returnOnEquity')
        ratios['roa'] = data.get('returnOnAssets')
        ratios['net_margin'] = data.get('profitMargins')
        ratios['gross_margin'] = data.get('grossMargins')
        ratios['operating_margin'] = data.get('operatingMargins')
        ratios['revenue_per_share'] = data.get('revenuePerShare')
        ratios['eps'] = data.get('trailingEps')
        
        # Financial health
        ratios['debt_to_equity'] = data.get('debtToEquity')
        ratios['current_ratio'] = data.get('currentRatio')
        ratios['quick_ratio'] = data.get('quickRatio')
        ratios['total_cash'] = data.get('totalCash')
        ratios['total_debt'] = data.get('totalDebt')
        ratios['free_cash_flow'] = data.get('freeCashflow')
        
        # Growth metrics
        ratios['revenue_growth'] = data.get('revenueGrowth')
        ratios['earnings_growth'] = data.get('earningsGrowth')
        ratios['quarterly_revenue_growth'] = data.get('revenueQuarterlyGrowth')
        ratios['quarterly_earnings_growth'] = data.get('earningsQuarterlyGrowth')
    except Exception as e:
        logging.error(f"Error fetching financial ratios: {str(e)}")
    return ratios


def fetch_price_data(ticker_obj: yf.Ticker) -> Dict:
    """Extract current price and trading statistics"""
    price_data = {}
    try:
        data = ticker_obj.info
        price_data['current_price'] = data.get('currentPrice') or data.get('regularMarketPrice')
        price_data['week_52_high'] = data.get('fiftyTwoWeekHigh')
        price_data['week_52_low'] = data.get('fiftyTwoWeekLow')
        price_data['day_high'] = data.get('dayHigh') or data.get('regularMarketDayHigh')
        price_data['day_low'] = data.get('dayLow') or data.get('regularMarketDayLow')
        price_data['previous_close'] = data.get('previousClose') or data.get('regularMarketPreviousClose')
        price_data['volume'] = data.get('volume') or data.get('regularMarketVolume')
        price_data['avg_volume'] = data.get('averageVolume')
        price_data['beta'] = data.get('beta')
    except Exception as e:
        logging.error(f"Error fetching price data: {str(e)}")
    return price_data


def fetch_dividend_info(ticker_obj: yf.Ticker) -> Dict:
    """Extract dividend-related information"""
    dividend_data = {}
    try:
        data = ticker_obj.info
        dividend_data['dividend_rate'] = data.get('dividendRate')
        dividend_data['dividend_yield'] = data.get('dividendYield')
        dividend_data['payout_ratio'] = data.get('payoutRatio')
        ex_div_date = data.get('exDividendDate')
        if ex_div_date:
            dividend_data['ex_dividend_date'] = datetime.fromtimestamp(ex_div_date)
        dividend_data['five_year_avg_dividend_yield'] = data.get('fiveYearAvgDividendYield')
    except Exception as e:
        logging.error(f"Error fetching dividend info: {str(e)}")
    return dividend_data


def fetch_financial_statements(ticker_obj: yf.Ticker) -> Dict:
    """Extract income statement, balance sheet, cash flow"""
    statements = {}
    try:
        statements['income_statement'] = ticker_obj.financials
        statements['balance_sheet'] = ticker_obj.balance_sheet
        statements['cash_flow'] = ticker_obj.cashflow
    except Exception as e:
        logging.error(f"Error fetching financial statements: {str(e)}")
    return statements


def fetch_analyst_data(ticker_obj: yf.Ticker) -> Dict:
    """Extract analyst recommendations and target prices"""
    analyst_data = {}
    try:
        data = ticker_obj.info
        analyst_data['target_price_mean'] = data.get('targetMeanPrice')
        analyst_data['target_price_high'] = data.get('targetHighPrice')
        analyst_data['target_price_low'] = data.get('targetLowPrice')
        analyst_data['num_analysts'] = data.get('numberOfAnalystOpinions')
        analyst_data['recommendation'] = data.get('recommendationKey')
        
        # Try to get recommendations
        try:
            recommendations = ticker_obj.recommendations
            if recommendations is not None and not recommendations.empty:
                analyst_data['analyst_ratings'] = recommendations
        except:
            pass
    except Exception as e:
        logging.error(f"Error fetching analyst data: {str(e)}")
    return analyst_data


def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """
    Fetch all data for a single stock
    Main entry point for data fetching
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        
        # Create StockData object
        stock_data = StockData(ticker=ticker)
        
        # Fetch all data components
        company_info = fetch_company_info(ticker_obj)
        ratios = fetch_financial_ratios(ticker_obj)
        price_data = fetch_price_data(ticker_obj)
        dividend_data = fetch_dividend_info(ticker_obj)
        statements = fetch_financial_statements(ticker_obj)
        analyst_data = fetch_analyst_data(ticker_obj)
        
        # Populate StockData object
        # Company info
        stock_data.company_name = company_info.get('company_name')
        stock_data.sector = company_info.get('sector')
        stock_data.industry = company_info.get('industry')
        stock_data.description = company_info.get('description')
        stock_data.website = company_info.get('website')
        stock_data.employees = company_info.get('employees')
        stock_data.headquarters = company_info.get('headquarters')
        stock_data.ceo = company_info.get('ceo')
        stock_data.market_cap = company_info.get('market_cap')
        
        # Ratios
        stock_data.pe_ratio = ratios.get('pe_ratio')
        stock_data.pb_ratio = ratios.get('pb_ratio')
        stock_data.peg_ratio = ratios.get('peg_ratio')
        stock_data.price_to_sales = ratios.get('price_to_sales')
        stock_data.enterprise_value = ratios.get('enterprise_value')
        stock_data.ev_to_ebitda = ratios.get('ev_to_ebitda')
        stock_data.roe = ratios.get('roe')
        stock_data.roa = ratios.get('roa')
        stock_data.net_margin = ratios.get('net_margin')
        stock_data.gross_margin = ratios.get('gross_margin')
        stock_data.operating_margin = ratios.get('operating_margin')
        stock_data.revenue_per_share = ratios.get('revenue_per_share')
        stock_data.eps = ratios.get('eps')
        stock_data.debt_to_equity = ratios.get('debt_to_equity')
        stock_data.current_ratio = ratios.get('current_ratio')
        stock_data.quick_ratio = ratios.get('quick_ratio')
        stock_data.total_cash = ratios.get('total_cash')
        stock_data.total_debt = ratios.get('total_debt')
        stock_data.free_cash_flow = ratios.get('free_cash_flow')
        stock_data.revenue_growth = ratios.get('revenue_growth')
        stock_data.earnings_growth = ratios.get('earnings_growth')
        stock_data.quarterly_revenue_growth = ratios.get('quarterly_revenue_growth')
        stock_data.quarterly_earnings_growth = ratios.get('quarterly_earnings_growth')
        
        # Price data
        stock_data.current_price = price_data.get('current_price')
        stock_data.week_52_high = price_data.get('week_52_high')
        stock_data.week_52_low = price_data.get('week_52_low')
        stock_data.day_high = price_data.get('day_high')
        stock_data.day_low = price_data.get('day_low')
        stock_data.previous_close = price_data.get('previous_close')
        stock_data.volume = price_data.get('volume')
        stock_data.avg_volume = price_data.get('avg_volume')
        stock_data.beta = price_data.get('beta')
        
        # Dividend data
        stock_data.dividend_rate = dividend_data.get('dividend_rate')
        stock_data.dividend_yield = dividend_data.get('dividend_yield')
        stock_data.payout_ratio = dividend_data.get('payout_ratio')
        stock_data.ex_dividend_date = dividend_data.get('ex_dividend_date')
        stock_data.five_year_avg_dividend_yield = dividend_data.get('five_year_avg_dividend_yield')
        
        # Financial statements
        stock_data.income_statement = statements.get('income_statement')
        stock_data.balance_sheet = statements.get('balance_sheet')
        stock_data.cash_flow = statements.get('cash_flow')
        
        # Analyst data
        stock_data.target_price_mean = analyst_data.get('target_price_mean')
        stock_data.target_price_high = analyst_data.get('target_price_high')
        stock_data.target_price_low = analyst_data.get('target_price_low')
        stock_data.num_analysts = analyst_data.get('num_analysts')
        stock_data.analyst_ratings = analyst_data.get('analyst_ratings')
        
        # Check if we got any valid data
        if not stock_data.company_name and not stock_data.current_price:
            return None
        
        return stock_data
        
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker}: {str(e)}")
        return None



# Configure logging
logging.basicConfig(
    filename='stock_analyzer.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



def fetch_peer_stocks(sector: str, exclude_ticker: str) -> List[str]:
    """
    Identify peer companies in same sector
    Note: This is a simplified implementation. In production, you would use
    a more sophisticated method to find peers.
    
    Args:
        sector: Sector name
        exclude_ticker: Ticker to exclude (the main stock)
    
    Returns:
        List of peer ticker symbols
    """
    from config import POPULAR_STOCKS, MAX_PEERS
    
    # This is a simplified implementation
    # In a real application, you would query a database or API for sector peers
    peers = []
    
    # For now, return empty list as we don't have a comprehensive peer database
    # This would need to be enhanced with actual sector-based stock lookup
    return peers[:MAX_PEERS]
