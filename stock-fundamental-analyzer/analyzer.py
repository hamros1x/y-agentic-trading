"""
Analyzer Module
Analysis logic, scoring, and flag detection
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from data_fetcher import StockData
import config


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
    red_flags: List[Tuple[str, str]]  # (flag_name, description)
    green_flags: List[Tuple[str, str]]



def calculate_investment_score(data: StockData) -> InvestmentScore:
    """
    Calculate 0-100 investment quality score
    
    Scoring breakdown:
    - P/E Ratio: max 30 points
    - ROE: max 20 points
    - Debt-to-Equity: max 20 points
    - Profit Margin: max 15 points
    - Revenue Growth: max 15 points
    """
    pe_score = 0
    roe_score = 0
    debt_score = 0
    margin_score = 0
    growth_score = 0
    missing_metrics = []
    
    # P/E Ratio Score (30 points max)
    if data.pe_ratio is not None and data.pe_ratio > 0:
        if data.pe_ratio < config.PE_EXCELLENT:
            pe_score = 30
        elif data.pe_ratio < config.PE_GOOD:
            pe_score = 20
        elif data.pe_ratio < config.PE_FAIR:
            pe_score = 10
        else:
            pe_score = 0
    else:
        missing_metrics.append('P/E Ratio')
    
    # ROE Score (20 points max)
    if data.roe is not None:
        roe_value = data.roe * 100 if data.roe < 1 else data.roe  # Convert to percentage if needed
        if roe_value > config.ROE_EXCELLENT:
            roe_score = 20
        elif roe_value > config.ROE_GOOD:
            roe_score = 15
        elif roe_value > config.ROE_FAIR:
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
        if de_value < config.DEBT_EXCELLENT:
            debt_score = 20
        elif de_value < config.DEBT_GOOD:
            debt_score = 15
        elif de_value < config.DEBT_FAIR:
            debt_score = 10
        else:
            debt_score = 0
    else:
        missing_metrics.append('Debt-to-Equity')
    
    # Profit Margin Score (15 points max)
    margin = data.net_margin
    if margin is not None:
        margin_value = margin * 100 if margin < 1 else margin  # Convert to percentage if needed
        if margin_value > config.MARGIN_EXCELLENT:
            margin_score = 15
        elif margin_value > config.MARGIN_GOOD:
            margin_score = 12
        elif margin_value > config.MARGIN_FAIR:
            margin_score = 8
        elif margin_value > 5:
            margin_score = 4
        else:
            margin_score = 0
    else:
        missing_metrics.append('Profit Margin')
    
    # Revenue Growth Score (15 points max)
    growth = data.revenue_growth
    if growth is not None:
        growth_value = growth * 100 if abs(growth) < 1 else growth  # Convert to percentage if needed
        if growth_value > config.GROWTH_EXCELLENT:
            growth_score = 15
        elif growth_value > config.GROWTH_GOOD:
            growth_score = 12
        elif growth_value > config.GROWTH_FAIR:
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
    """
    Detect warning indicators
    
    Red flags:
    - Debt-to-Equity > 2.0
    - Negative ROE
    - Declining revenue (YoY)
    - Negative profit margins
    - P/E > 50
    - Negative cash flow
    """
    red_flags = []
    
    # High debt
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        if de_value > config.RED_FLAG_DEBT:
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
    
    # High P/E (potentially overvalued)
    if data.pe_ratio is not None and data.pe_ratio > config.RED_FLAG_PE:
        red_flags.append(("High P/E Ratio", f"P/E ratio of {data.pe_ratio:.2f} may indicate overvaluation"))
    
    # Negative cash flow
    if data.free_cash_flow is not None and data.free_cash_flow < 0:
        red_flags.append(("Negative Cash Flow", "Company is burning cash"))
    
    return red_flags


def identify_green_flags(data: StockData) -> List[Tuple[str, str]]:
    """
    Detect positive indicators
    
    Green flags:
    - ROE > 15%
    - Low debt (D/E < 0.5)
    - Revenue growth > 10%
    - Strong profit margins (>15%)
    - Positive free cash flow
    - Reasonable P/E (10-25)
    """
    green_flags = []
    
    # Strong ROE
    if data.roe is not None:
        roe_value = data.roe * 100 if abs(data.roe) < 1 else data.roe
        if roe_value > config.GREEN_FLAG_ROE:
            green_flags.append(("Strong ROE", f"Return on Equity of {roe_value:.2f}% shows efficient use of capital"))
    
    # Low debt
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        if de_value < config.GREEN_FLAG_DEBT:
            green_flags.append(("Low Debt", f"Debt-to-Equity ratio of {de_value:.2f} indicates strong balance sheet"))
    
    # Strong revenue growth
    if data.revenue_growth is not None:
        growth_value = data.revenue_growth * 100 if abs(data.revenue_growth) < 1 else data.revenue_growth
        if growth_value > config.GREEN_FLAG_GROWTH:
            green_flags.append(("Strong Growth", f"Revenue grew by {growth_value:.2f}% year-over-year"))
    
    # Healthy profit margins
    if data.net_margin is not None:
        margin_value = data.net_margin * 100 if abs(data.net_margin) < 1 else data.net_margin
        if margin_value > config.GREEN_FLAG_MARGIN:
            green_flags.append(("Healthy Margins", f"Net profit margin of {margin_value:.2f}% shows strong profitability"))
    
    # Positive free cash flow
    if data.free_cash_flow is not None and data.free_cash_flow > 0:
        green_flags.append(("Positive Cash Flow", "Company generates positive free cash flow"))
    
    # Reasonable P/E
    if data.pe_ratio is not None:
        if config.GREEN_FLAG_PE_MIN <= data.pe_ratio <= config.GREEN_FLAG_PE_MAX:
            green_flags.append(("Reasonable Valuation", f"P/E ratio of {data.pe_ratio:.2f} is in fair value range"))
    
    return green_flags



def interpret_ratio(ratio_name: str, value: float, industry_avg: Optional[float] = None) -> str:
    """
    Provide contextual interpretation for a ratio
    
    Args:
        ratio_name: Name of the ratio
        value: Value of the ratio
        industry_avg: Optional industry average for comparison
    
    Returns:
        Interpretation string
    """
    if value is None:
        return "Data not available"
    
    interpretations = {
        'pe_ratio': _interpret_pe,
        'pb_ratio': _interpret_pb,
        'roe': _interpret_roe,
        'debt_to_equity': _interpret_debt,
        'current_ratio': _interpret_current_ratio,
        'profit_margin': _interpret_margin,
        'revenue_growth': _interpret_growth,
        'beta': _interpret_beta
    }
    
    interpreter = interpretations.get(ratio_name.lower())
    if interpreter:
        return interpreter(value)
    else:
        return ""


def _interpret_pe(value: float) -> str:
    """Interpret P/E ratio"""
    if value < 0:
        return "Negative P/E indicates losses"
    elif value < 15:
        return "Below market average - potentially undervalued or facing challenges"
    elif value < 25:
        return "Fairly valued - in line with market average"
    elif value < 35:
        return "Above average - market expects growth or stock may be overvalued"
    else:
        return "High P/E - expensive valuation or very high growth expectations"


def _interpret_pb(value: float) -> str:
    """Interpret P/B ratio"""
    if value < 1:
        return "Trading below book value - potentially undervalued"
    elif value < 3:
        return "Reasonable valuation relative to book value"
    else:
        return "Trading at premium to book value - growth expectations or intangible assets"


def _interpret_roe(value: float) -> str:
    """Interpret ROE"""
    roe_pct = value * 100 if abs(value) < 1 else value
    if roe_pct < 0:
        return "Negative ROE indicates company is losing money"
    elif roe_pct < 10:
        return "Below average - company not efficiently using shareholder capital"
    elif roe_pct < 15:
        return "Average - decent returns on equity"
    elif roe_pct < 20:
        return "Good - company efficiently generates profits from equity"
    else:
        return "Excellent - very efficient use of shareholder capital"


def _interpret_debt(value: float) -> str:
    """Interpret Debt-to-Equity ratio"""
    de_value = value / 100 if value > 10 else value
    if de_value < 0.5:
        return "Low debt - strong balance sheet with minimal leverage"
    elif de_value < 1.0:
        return "Moderate debt - balanced capital structure"
    elif de_value < 2.0:
        return "High debt - company is leveraged, monitor carefully"
    else:
        return "Very high debt - significant financial risk"


def _interpret_current_ratio(value: float) -> str:
    """Interpret Current Ratio"""
    if value < 1.0:
        return "Below 1.0 - may have liquidity issues"
    elif value < 1.5:
        return "Adequate liquidity to meet short-term obligations"
    else:
        return "Strong liquidity position"


def _interpret_margin(value: float) -> str:
    """Interpret Profit Margin"""
    margin_pct = value * 100 if abs(value) < 1 else value
    if margin_pct < 0:
        return "Negative margin - company is unprofitable"
    elif margin_pct < 5:
        return "Low margins - thin profitability"
    elif margin_pct < 10:
        return "Moderate margins - decent profitability"
    elif margin_pct < 20:
        return "Good margins - strong profitability"
    else:
        return "Excellent margins - very profitable operations"


def _interpret_growth(value: float) -> str:
    """Interpret Revenue Growth"""
    growth_pct = value * 100 if abs(value) < 1 else value
    if growth_pct < 0:
        return "Declining revenue - concerning trend"
    elif growth_pct < 5:
        return "Slow growth - mature or struggling business"
    elif growth_pct < 15:
        return "Moderate growth - healthy expansion"
    elif growth_pct < 25:
        return "Strong growth - rapidly expanding"
    else:
        return "Very high growth - exceptional expansion"


def _interpret_beta(value: float) -> str:
    """Interpret Beta"""
    if value < 0.5:
        return "Low volatility - stock moves less than market"
    elif value < 1.0:
        return "Below market volatility - relatively stable"
    elif value < 1.5:
        return "Above market volatility - more volatile than market"
    else:
        return "High volatility - significantly more volatile than market"



def categorize_market_cap(market_cap: float) -> str:
    """
    Categorize market cap as Large/Mid/Small cap
    
    Args:
        market_cap: Market capitalization in INR
    
    Returns:
        Category string
    """
    if market_cap is None:
        return "Unknown"
    
    if market_cap >= config.LARGE_CAP_MIN:
        return "Large Cap"
    elif market_cap >= config.MID_CAP_MIN:
        return "Mid Cap"
    else:
        return "Small Cap"


def calculate_growth_rate(current: float, previous: float) -> Optional[float]:
    """
    Calculate year-over-year growth percentage
    
    Args:
        current: Current period value
        previous: Previous period value
    
    Returns:
        Growth rate as percentage or None
    """
    if current is None or previous is None or previous == 0:
        return None
    
    return ((current - previous) / abs(previous)) * 100
