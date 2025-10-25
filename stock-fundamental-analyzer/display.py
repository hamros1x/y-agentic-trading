"""
Display Module
Console output formatting and presentation
"""

from colorama import Fore, Style, init
from typing import List, Optional
from data_fetcher import StockData
from analyzer import InvestmentScore, FlagAnalysis
import utils
import config

# Initialize colorama for Windows compatibility
init(autoreset=True)


def print_section_header(title: str) -> None:
    """Print formatted section header with borders"""
    width = 64
    print(f"\n{Fore.CYAN}╔{'═' * (width - 2)}╗")
    print(f"║{title.center(width - 2)}║")
    print(f"╚{'═' * (width - 2)}╝{Style.RESET_ALL}")


def print_metric(label: str, value: str, interpretation: str = None, color: str = Fore.WHITE) -> None:
    """Print formatted metric line"""
    print(f"{color}{label}: {value}{Style.RESET_ALL}")
    if interpretation:
        print(f"  {Fore.YELLOW}└─ {interpretation}{Style.RESET_ALL}")


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    """Print formatted table"""
    if not rows:
        return
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"{Fore.CYAN}{header_line}{Style.RESET_ALL}")
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(row_line)



def display_company_overview(data: StockData) -> None:
    """Display formatted company information"""
    from analyzer import categorize_market_cap
    
    print_section_header("COMPANY OVERVIEW")
    
    if data.company_name:
        print(f"Name: {Fore.WHITE}{data.company_name}{Style.RESET_ALL}")
    
    if data.sector:
        print(f"Sector: {data.sector}")
    
    if data.industry:
        print(f"Industry: {data.industry}")
    
    if data.market_cap:
        category = categorize_market_cap(data.market_cap)
        print(f"Market Cap: {utils.format_large_number(data.market_cap)} ({category})")
    
    if data.employees:
        print(f"Employees: {data.employees:,}")
    
    if data.headquarters:
        print(f"Headquarters: {data.headquarters}")
    
    if data.website:
        print(f"Website: {data.website}")
    
    if data.ceo:
        print(f"CEO: {data.ceo}")
    
    if data.description:
        desc = utils.truncate_text(data.description, 300)
        print(f"\nBusiness: {desc}")



def display_valuation_ratios(data: StockData) -> None:
    """Display valuation metrics with interpretations"""
    from analyzer import interpret_ratio
    
    print_section_header("VALUATION RATIOS")
    
    if data.pe_ratio is not None:
        interp = interpret_ratio('pe_ratio', data.pe_ratio)
        print_metric("P/E Ratio", f"{data.pe_ratio:.2f}", interp)
    else:
        print_metric("P/E Ratio", "N/A")
    
    if data.pb_ratio is not None:
        interp = interpret_ratio('pb_ratio', data.pb_ratio)
        print_metric("P/B Ratio", f"{data.pb_ratio:.2f}", interp)
    else:
        print_metric("P/B Ratio", "N/A")
    
    if data.peg_ratio is not None:
        print_metric("PEG Ratio", f"{data.peg_ratio:.2f}")
    else:
        print_metric("PEG Ratio", "N/A")
    
    if data.price_to_sales is not None:
        print_metric("Price to Sales", f"{data.price_to_sales:.2f}")
    else:
        print_metric("Price to Sales", "N/A")
    
    if data.enterprise_value is not None:
        print_metric("Enterprise Value", utils.format_large_number(data.enterprise_value))
    else:
        print_metric("Enterprise Value", "N/A")
    
    if data.ev_to_ebitda is not None:
        print_metric("EV/EBITDA", f"{data.ev_to_ebitda:.2f}")
    else:
        print_metric("EV/EBITDA", "N/A")


def display_profitability_metrics(data: StockData) -> None:
    """Display profitability indicators"""
    from analyzer import interpret_ratio
    
    print_section_header("PROFITABILITY METRICS")
    
    if data.roe is not None:
        roe_pct = data.roe * 100 if abs(data.roe) < 1 else data.roe
        interp = interpret_ratio('roe', data.roe)
        color = Fore.GREEN if roe_pct > 15 else Fore.YELLOW if roe_pct > 10 else Fore.RED
        print_metric("ROE (Return on Equity)", f"{roe_pct:.2f}%", interp, color)
    else:
        print_metric("ROE (Return on Equity)", "N/A")
    
    if data.roa is not None:
        roa_pct = data.roa * 100 if abs(data.roa) < 1 else data.roa
        print_metric("ROA (Return on Assets)", f"{roa_pct:.2f}%")
    else:
        print_metric("ROA (Return on Assets)", "N/A")
    
    if data.net_margin is not None:
        margin_pct = data.net_margin * 100 if abs(data.net_margin) < 1 else data.net_margin
        interp = interpret_ratio('profit_margin', data.net_margin)
        color = Fore.GREEN if margin_pct > 15 else Fore.YELLOW if margin_pct > 5 else Fore.RED
        print_metric("Net Profit Margin", f"{margin_pct:.2f}%", interp, color)
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
    
    if data.eps is not None:
        print_metric("EPS (Earnings Per Share)", f"₹{data.eps:.2f}")
    else:
        print_metric("EPS (Earnings Per Share)", "N/A")
    
    if data.revenue_per_share is not None:
        print_metric("Revenue Per Share", f"₹{data.revenue_per_share:.2f}")
    else:
        print_metric("Revenue Per Share", "N/A")


def display_financial_health(data: StockData) -> None:
    """Display debt, liquidity, and cash metrics"""
    from analyzer import interpret_ratio
    
    print_section_header("FINANCIAL HEALTH")
    
    if data.debt_to_equity is not None:
        de_value = data.debt_to_equity / 100 if data.debt_to_equity > 10 else data.debt_to_equity
        interp = interpret_ratio('debt_to_equity', de_value)
        color = Fore.GREEN if de_value < 0.5 else Fore.YELLOW if de_value < 1.5 else Fore.RED
        print_metric("Debt-to-Equity Ratio", f"{de_value:.2f}", interp, color)
    else:
        print_metric("Debt-to-Equity Ratio", "N/A")
    
    if data.current_ratio is not None:
        interp = interpret_ratio('current_ratio', data.current_ratio)
        print_metric("Current Ratio", f"{data.current_ratio:.2f}", interp)
    else:
        print_metric("Current Ratio", "N/A")
    
    if data.quick_ratio is not None:
        print_metric("Quick Ratio", f"{data.quick_ratio:.2f}")
    else:
        print_metric("Quick Ratio", "N/A")
    
    if data.total_cash is not None:
        print_metric("Total Cash", utils.format_large_number(data.total_cash))
    else:
        print_metric("Total Cash", "N/A")
    
    if data.total_debt is not None:
        print_metric("Total Debt", utils.format_large_number(data.total_debt))
    else:
        print_metric("Total Debt", "N/A")
    
    if data.free_cash_flow is not None:
        color = Fore.GREEN if data.free_cash_flow > 0 else Fore.RED
        print_metric("Free Cash Flow", utils.format_large_number(data.free_cash_flow), color=color)
    else:
        print_metric("Free Cash Flow", "N/A")


def display_growth_metrics(data: StockData) -> None:
    """Display growth rates"""
    from analyzer import interpret_ratio
    
    print_section_header("GROWTH METRICS")
    
    if data.revenue_growth is not None:
        growth_pct = data.revenue_growth * 100 if abs(data.revenue_growth) < 1 else data.revenue_growth
        interp = interpret_ratio('revenue_growth', data.revenue_growth)
        color = Fore.GREEN if growth_pct > 10 else Fore.YELLOW if growth_pct > 0 else Fore.RED
        print_metric("Revenue Growth (YoY)", f"{growth_pct:.2f}%", interp, color)
    else:
        print_metric("Revenue Growth (YoY)", "N/A")
    
    if data.earnings_growth is not None:
        earn_pct = data.earnings_growth * 100 if abs(data.earnings_growth) < 1 else data.earnings_growth
        color = Fore.GREEN if earn_pct > 10 else Fore.YELLOW if earn_pct > 0 else Fore.RED
        print_metric("Earnings Growth (YoY)", f"{earn_pct:.2f}%", color=color)
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
    from analyzer import interpret_ratio
    
    print_section_header("STOCK PRICE ANALYSIS")
    
    if data.current_price is not None:
        print_metric("Current Price", f"₹{data.current_price:.2f}")
    else:
        print_metric("Current Price", "N/A")
    
    if data.previous_close is not None:
        print_metric("Previous Close", f"₹{data.previous_close:.2f}")
    else:
        print_metric("Previous Close", "N/A")
    
    if data.day_high is not None and data.day_low is not None:
        print_metric("Day's Range", f"₹{data.day_low:.2f} - ₹{data.day_high:.2f}")
    else:
        print_metric("Day's Range", "N/A")
    
    if data.week_52_high is not None:
        print_metric("52-Week High", f"₹{data.week_52_high:.2f}")
        if data.current_price:
            pct_from_high = ((data.current_price - data.week_52_high) / data.week_52_high) * 100
            print(f"  {Fore.YELLOW}└─ {pct_from_high:+.2f}% from 52-week high{Style.RESET_ALL}")
    else:
        print_metric("52-Week High", "N/A")
    
    if data.week_52_low is not None:
        print_metric("52-Week Low", f"₹{data.week_52_low:.2f}")
        if data.current_price:
            pct_from_low = ((data.current_price - data.week_52_low) / data.week_52_low) * 100
            print(f"  {Fore.YELLOW}└─ {pct_from_low:+.2f}% from 52-week low{Style.RESET_ALL}")
    else:
        print_metric("52-Week Low", "N/A")
    
    if data.volume is not None:
        print_metric("Volume", f"{int(data.volume):,}")
    else:
        print_metric("Volume", "N/A")
    
    if data.avg_volume is not None:
        print_metric("Average Volume", f"{int(data.avg_volume):,}")
    else:
        print_metric("Average Volume", "N/A")
    
    if data.beta is not None:
        interp = interpret_ratio('beta', data.beta)
        print_metric("Beta (Volatility)", f"{data.beta:.2f}", interp)
    else:
        print_metric("Beta (Volatility)", "N/A")


def display_dividend_info(data: StockData) -> None:
    """Display dividend information"""
    print_section_header("DIVIDEND INFORMATION")
    
    has_dividend = any([
        data.dividend_rate,
        data.dividend_yield,
        data.payout_ratio
    ])
    
    if not has_dividend:
        print(f"{Fore.YELLOW}No dividend information available for this stock{Style.RESET_ALL}")
        return
    
    if data.dividend_rate is not None:
        print_metric("Dividend Rate (Annual)", f"₹{data.dividend_rate:.2f}")
    else:
        print_metric("Dividend Rate (Annual)", "N/A")
    
    if data.dividend_yield is not None:
        yield_pct = data.dividend_yield * 100 if data.dividend_yield < 1 else data.dividend_yield
        print_metric("Dividend Yield", f"{yield_pct:.2f}%")
    else:
        print_metric("Dividend Yield", "N/A")
    
    if data.payout_ratio is not None:
        payout_pct = data.payout_ratio * 100 if data.payout_ratio < 1 else data.payout_ratio
        print_metric("Payout Ratio", f"{payout_pct:.2f}%")
    else:
        print_metric("Payout Ratio", "N/A")
    
    if data.ex_dividend_date is not None:
        print_metric("Ex-Dividend Date", data.ex_dividend_date.strftime("%Y-%m-%d"))
    else:
        print_metric("Ex-Dividend Date", "N/A")
    
    if data.five_year_avg_dividend_yield is not None:
        avg_yield_pct = data.five_year_avg_dividend_yield * 100 if data.five_year_avg_dividend_yield < 1 else data.five_year_avg_dividend_yield
        print_metric("5-Year Avg Dividend Yield", f"{avg_yield_pct:.2f}%")
    else:
        print_metric("5-Year Avg Dividend Yield", "N/A")



def display_financial_statements(data: StockData) -> None:
    """Display income statement, balance sheet, cash flow as tables"""
    import pandas as pd
    
    # Income Statement
    if data.income_statement is not None and not data.income_statement.empty:
        print_section_header("INCOME STATEMENT (Last 3-4 Years)")
        
        try:
            # Get key metrics from income statement
            metrics_to_show = [
                'Total Revenue',
                'Cost Of Revenue',
                'Gross Profit',
                'Operating Expense',
                'Operating Income',
                'Net Income'
            ]
            
            # Display as simplified table
            df = data.income_statement
            years = df.columns[:4] if len(df.columns) >= 4 else df.columns
            
            print(f"\n{Fore.CYAN}Key Metrics (in Crores):{Style.RESET_ALL}")
            for metric in metrics_to_show:
                if metric in df.index:
                    print(f"\n{metric}:")
                    for year in years:
                        value = df.loc[metric, year]
                        year_str = str(year)[:10]  # Format date
                        print(f"  {year_str}: {utils.format_large_number(value)}")
        except Exception as e:
            print(f"{Fore.YELLOW}Unable to display income statement details{Style.RESET_ALL}")
    
    # Balance Sheet
    if data.balance_sheet is not None and not data.balance_sheet.empty:
        print_section_header("BALANCE SHEET (Last 3-4 Years)")
        
        try:
            metrics_to_show = [
                'Total Assets',
                'Total Liabilities Net Minority Interest',
                'Stockholders Equity',
                'Cash And Cash Equivalents',
                'Total Debt'
            ]
            
            df = data.balance_sheet
            years = df.columns[:4] if len(df.columns) >= 4 else df.columns
            
            print(f"\n{Fore.CYAN}Key Metrics (in Crores):{Style.RESET_ALL}")
            for metric in metrics_to_show:
                if metric in df.index:
                    print(f"\n{metric}:")
                    for year in years:
                        value = df.loc[metric, year]
                        year_str = str(year)[:10]
                        print(f"  {year_str}: {utils.format_large_number(value)}")
        except Exception as e:
            print(f"{Fore.YELLOW}Unable to display balance sheet details{Style.RESET_ALL}")
    
    # Cash Flow Statement
    if data.cash_flow is not None and not data.cash_flow.empty:
        print_section_header("CASH FLOW STATEMENT (Last 3-4 Years)")
        
        try:
            metrics_to_show = [
                'Operating Cash Flow',
                'Investing Cash Flow',
                'Financing Cash Flow',
                'Free Cash Flow'
            ]
            
            df = data.cash_flow
            years = df.columns[:4] if len(df.columns) >= 4 else df.columns
            
            print(f"\n{Fore.CYAN}Key Metrics (in Crores):{Style.RESET_ALL}")
            for metric in metrics_to_show:
                if metric in df.index:
                    print(f"\n{metric}:")
                    for year in years:
                        value = df.loc[metric, year]
                        year_str = str(year)[:10]
                        print(f"  {year_str}: {utils.format_large_number(value)}")
        except Exception as e:
            print(f"{Fore.YELLOW}Unable to display cash flow details{Style.RESET_ALL}")



def display_analyst_recommendations(data: StockData) -> None:
    """Display analyst ratings and target prices"""
    print_section_header("ANALYST RECOMMENDATIONS")
    
    has_analyst_data = any([
        data.target_price_mean,
        data.target_price_high,
        data.target_price_low,
        data.num_analysts
    ])
    
    if not has_analyst_data:
        print(f"{Fore.YELLOW}Analyst recommendations not available for this stock{Style.RESET_ALL}")
        return
    
    if data.num_analysts is not None:
        print_metric("Number of Analysts", str(data.num_analysts))
    
    if data.target_price_mean is not None:
        print_metric("Target Price (Mean)", f"₹{data.target_price_mean:.2f}")
    else:
        print_metric("Target Price (Mean)", "N/A")
    
    if data.target_price_high is not None:
        print_metric("Target Price (High)", f"₹{data.target_price_high:.2f}")
    else:
        print_metric("Target Price (High)", "N/A")
    
    if data.target_price_low is not None:
        print_metric("Target Price (Low)", f"₹{data.target_price_low:.2f}")
    else:
        print_metric("Target Price (Low)", "N/A")
    
    # Show potential upside/downside
    if data.target_price_mean and data.current_price:
        potential = ((data.target_price_mean - data.current_price) / data.current_price) * 100
        color = Fore.GREEN if potential > 0 else Fore.RED
        print(f"\n{color}Potential: {potential:+.2f}% from current price{Style.RESET_ALL}")


def display_peer_comparison(main_stock: StockData, peers: List[StockData]) -> None:
    """Display comparison table"""
    if not peers:
        return
    
    print_section_header("PEER COMPARISON")
    
    # Prepare comparison data
    headers = ["Metric", main_stock.ticker] + [p.ticker for p in peers]
    rows = []
    
    # Market Cap
    row = ["Market Cap"]
    row.append(utils.format_large_number(main_stock.market_cap) if main_stock.market_cap else "N/A")
    for peer in peers:
        row.append(utils.format_large_number(peer.market_cap) if peer.market_cap else "N/A")
    rows.append(row)
    
    # P/E Ratio
    row = ["P/E Ratio"]
    row.append(f"{main_stock.pe_ratio:.2f}" if main_stock.pe_ratio else "N/A")
    for peer in peers:
        row.append(f"{peer.pe_ratio:.2f}" if peer.pe_ratio else "N/A")
    rows.append(row)
    
    # ROE
    row = ["ROE (%)"]
    if main_stock.roe:
        roe_val = main_stock.roe * 100 if abs(main_stock.roe) < 1 else main_stock.roe
        row.append(f"{roe_val:.2f}%")
    else:
        row.append("N/A")
    for peer in peers:
        if peer.roe:
            roe_val = peer.roe * 100 if abs(peer.roe) < 1 else peer.roe
            row.append(f"{roe_val:.2f}%")
        else:
            row.append("N/A")
    rows.append(row)
    
    # Profit Margin
    row = ["Profit Margin (%)"]
    if main_stock.net_margin:
        margin_val = main_stock.net_margin * 100 if abs(main_stock.net_margin) < 1 else main_stock.net_margin
        row.append(f"{margin_val:.2f}%")
    else:
        row.append("N/A")
    for peer in peers:
        if peer.net_margin:
            margin_val = peer.net_margin * 100 if abs(peer.net_margin) < 1 else peer.net_margin
            row.append(f"{margin_val:.2f}%")
        else:
            row.append("N/A")
    rows.append(row)
    
    print_table(headers, rows)



def display_investment_score(score: InvestmentScore) -> None:
    """Display score with visual indicator and interpretation"""
    print_section_header("INVESTMENT QUALITY SCORE")
    
    # Determine color based on score
    if score.total_score >= 80:
        color = Fore.GREEN
    elif score.total_score >= 60:
        color = Fore.CYAN
    elif score.total_score >= 40:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    
    # Display total score
    print(f"\n{color}{'█' * int(score.total_score / 5)} {score.total_score:.0f}/100{Style.RESET_ALL}")
    print(f"{color}{score.interpretation}{Style.RESET_ALL}\n")
    
    # Display breakdown
    print(f"{Fore.CYAN}Score Breakdown:{Style.RESET_ALL}")
    print(f"  P/E Ratio Score:      {score.pe_score:.0f}/30")
    print(f"  ROE Score:            {score.roe_score:.0f}/20")
    print(f"  Debt-to-Equity Score: {score.debt_score:.0f}/20")
    print(f"  Profit Margin Score:  {score.margin_score:.0f}/15")
    print(f"  Revenue Growth Score: {score.growth_score:.0f}/15")
    
    # Show missing metrics if any
    if score.missing_metrics:
        print(f"\n{Fore.YELLOW}Note: Score calculated without: {', '.join(score.missing_metrics)}{Style.RESET_ALL}")


def display_flags(flags: FlagAnalysis) -> None:
    """Display red and green flags with color coding"""
    
    # Display Red Flags
    print_section_header("⚠️  RED FLAGS (Warning Signs)")
    
    if flags.red_flags:
        for flag_name, description in flags.red_flags:
            print(f"{Fore.RED}❌ {flag_name}{Style.RESET_ALL}")
            print(f"   {description}\n")
    else:
        print(f"{Fore.GREEN}✓ No major red flags detected{Style.RESET_ALL}\n")
    
    # Display Green Flags
    print_section_header("✓  GREEN FLAGS (Positive Signs)")
    
    if flags.green_flags:
        for flag_name, description in flags.green_flags:
            print(f"{Fore.GREEN}✓ {flag_name}{Style.RESET_ALL}")
            print(f"   {description}\n")
    else:
        print(f"{Fore.YELLOW}No significant green flags detected{Style.RESET_ALL}\n")



def display_comparison_table(stocks: List[StockData]) -> None:
    """Display side-by-side stock comparison"""
    if not stocks or len(stocks) < 2:
        print(f"{Fore.YELLOW}Need at least 2 stocks for comparison{Style.RESET_ALL}")
        return
    
    print_section_header("MULTI-STOCK COMPARISON")
    
    # Prepare headers
    headers = ["Metric"] + [stock.ticker for stock in stocks]
    rows = []
    
    # Company Name
    row = ["Company"]
    for stock in stocks:
        name = stock.company_name[:20] if stock.company_name else "N/A"
        row.append(name)
    rows.append(row)
    
    # Market Cap
    row = ["Market Cap"]
    for stock in stocks:
        row.append(utils.format_large_number(stock.market_cap) if stock.market_cap else "N/A")
    rows.append(row)
    
    # P/E Ratio
    row = ["P/E Ratio"]
    for stock in stocks:
        row.append(f"{stock.pe_ratio:.2f}" if stock.pe_ratio else "N/A")
    rows.append(row)
    
    # ROE
    row = ["ROE (%)"]
    for stock in stocks:
        if stock.roe:
            roe_val = stock.roe * 100 if abs(stock.roe) < 1 else stock.roe
            row.append(f"{roe_val:.2f}")
        else:
            row.append("N/A")
    rows.append(row)
    
    # Debt-to-Equity
    row = ["Debt/Equity"]
    for stock in stocks:
        if stock.debt_to_equity:
            de_val = stock.debt_to_equity / 100 if stock.debt_to_equity > 10 else stock.debt_to_equity
            row.append(f"{de_val:.2f}")
        else:
            row.append("N/A")
    rows.append(row)
    
    # Profit Margin
    row = ["Profit Margin (%)"]
    for stock in stocks:
        if stock.net_margin:
            margin_val = stock.net_margin * 100 if abs(stock.net_margin) < 1 else stock.net_margin
            row.append(f"{margin_val:.2f}")
        else:
            row.append("N/A")
    rows.append(row)
    
    # Revenue Growth
    row = ["Revenue Growth (%)"]
    for stock in stocks:
        if stock.revenue_growth:
            growth_val = stock.revenue_growth * 100 if abs(stock.revenue_growth) < 1 else stock.revenue_growth
            row.append(f"{growth_val:.2f}")
        else:
            row.append("N/A")
    rows.append(row)
    
    # Current Price
    row = ["Current Price"]
    for stock in stocks:
        row.append(f"₹{stock.current_price:.2f}" if stock.current_price else "N/A")
    rows.append(row)
    
    print_table(headers, rows)
    
    # Calculate and display investment scores
    print(f"\n{Fore.CYAN}Investment Quality Scores:{Style.RESET_ALL}")
    from analyzer import calculate_investment_score
    for stock in stocks:
        score = calculate_investment_score(stock)
        color = Fore.GREEN if score.total_score >= 60 else Fore.YELLOW if score.total_score >= 40 else Fore.RED
        print(f"{stock.ticker}: {color}{score.total_score:.0f}/100 - {score.interpretation}{Style.RESET_ALL}")


