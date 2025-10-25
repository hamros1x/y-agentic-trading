"""
Stock Fundamental Analyzer - Main Entry Point
Indian Stock Market (NSE/BSE) Analysis Tool
"""

from colorama import Fore, Style, init
import sys
from data_fetcher import fetch_stock_data
from analyzer import calculate_investment_score, identify_red_flags, identify_green_flags, FlagAnalysis
import display
import charts
import utils
import config

# Initialize colorama
init(autoreset=True)


def display_main_menu() -> None:
    """Display main menu and return user choice"""
    print(f"\n{Fore.CYAN}╔════════════════════════════════════════╗")
    print(f"║  STOCK FUNDAMENTAL ANALYZER v1.0       ║")
    print(f"║  Indian Stock Market (NSE/BSE)         ║")
    print(f"╚════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    print("1. Analyze Single Stock")
    print("2. Compare Multiple Stocks (2-5 stocks)")
    print("3. View Saved Reports")
    print("4. Help (How to read fundamental data)")
    print("5. Exit")
    print()



def analyze_single_stock_flow() -> None:
    """Orchestrate complete single stock analysis"""
    print(f"\n{Fore.CYAN}=== Single Stock Analysis ==={Style.RESET_ALL}\n")
    
    # Get ticker from user
    ticker_input = input("Enter stock symbol (e.g., RELIANCE.NS, TCS.NS): ").strip()
    
    # Validate ticker
    is_valid, error_msg = utils.validate_ticker(ticker_input)
    if not is_valid:
        print(f"\n{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        return
    
    ticker = utils.normalize_ticker(ticker_input)
    
    # Fetch data
    print(f"\n{Fore.YELLOW}Fetching fundamental data for {ticker}...{Style.RESET_ALL}")
    
    try:
        stock_data = fetch_stock_data(ticker)
        
        if stock_data is None:
            print(f"\n{Fore.RED}❌ Unable to fetch data for {ticker}.{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Suggestions:")
            print(f"• Check if the stock symbol is correct (e.g., RELIANCE.NS for NSE)")
            print(f"• Verify the stock is listed on NSE (.NS) or BSE (.BO)")
            print(f"• Ensure your internet connection is active")
            print(f"• Try again in a few moments if the service is busy{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}✓ Data retrieved successfully{Style.RESET_ALL}\n")
        
        # Display all sections
        display.display_company_overview(stock_data)
        display.display_valuation_ratios(stock_data)
        display.display_profitability_metrics(stock_data)
        display.display_financial_health(stock_data)
        display.display_growth_metrics(stock_data)
        display.display_price_analysis(stock_data)
        display.display_dividend_info(stock_data)
        
        # Calculate and display score
        score = calculate_investment_score(stock_data)
        display.display_investment_score(score)
        
        # Identify and display flags
        red_flags = identify_red_flags(stock_data)
        green_flags = identify_green_flags(stock_data)
        flags = FlagAnalysis(red_flags=red_flags, green_flags=green_flags)
        display.display_flags(flags)
        
        # Display financial statements
        display.display_financial_statements(stock_data)
        
        # Display analyst recommendations
        display.display_analyst_recommendations(stock_data)
        
        # Generate charts
        print(f"\n{Fore.YELLOW}Generating charts...{Style.RESET_ALL}")
        chart_paths = charts.generate_all_charts(stock_data, ticker)
        if chart_paths:
            print(f"{Fore.GREEN}✓ Generated {len(chart_paths)} chart(s){Style.RESET_ALL}")
            print(f"Charts saved in: {config.CHARTS_DIR}/{ticker}/")
        else:
            print(f"{Fore.YELLOW}No charts generated (insufficient historical data){Style.RESET_ALL}")
        
        # Offer to save report
        save_choice = input(f"\n{Fore.CYAN}Save analysis report? (y/n): {Style.RESET_ALL}").strip().lower()
        if save_choice == 'y':
            # Build report content
            report_content = build_report(stock_data, score, flags, chart_paths)
            try:
                filepath = utils.save_report(report_content, ticker)
                print(f"{Fore.GREEN}✓ Report saved: {filepath}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Failed to save report: {str(e)}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ An error occurred: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please try again or contact support if the issue persists.{Style.RESET_ALL}")



def compare_stocks_flow() -> None:
    """Handle multi-stock comparison"""
    print(f"\n{Fore.CYAN}=== Multi-Stock Comparison ==={Style.RESET_ALL}\n")
    
    # Get tickers from user
    tickers_input = input("Enter 2-5 stock symbols separated by commas (e.g., RELIANCE.NS, TCS.NS, INFY.NS): ").strip()
    ticker_list = [t.strip() for t in tickers_input.split(',')]
    
    if len(ticker_list) < 2:
        print(f"\n{Fore.RED}❌ Please enter at least 2 stock symbols{Style.RESET_ALL}")
        return
    
    if len(ticker_list) > 5:
        print(f"\n{Fore.YELLOW}⚠ Maximum 5 stocks allowed. Using first 5...{Style.RESET_ALL}")
        ticker_list = ticker_list[:5]
    
    # Validate and normalize tickers
    valid_tickers = []
    for ticker_input in ticker_list:
        is_valid, error_msg = utils.validate_ticker(ticker_input)
        if is_valid:
            valid_tickers.append(utils.normalize_ticker(ticker_input))
        else:
            print(f"{Fore.YELLOW}⚠ Skipping invalid ticker: {ticker_input} - {error_msg}{Style.RESET_ALL}")
    
    if len(valid_tickers) < 2:
        print(f"\n{Fore.RED}❌ Need at least 2 valid stock symbols for comparison{Style.RESET_ALL}")
        return
    
    # Fetch data for all stocks
    stocks_data = []
    for ticker in valid_tickers:
        print(f"\n{Fore.YELLOW}Fetching data for {ticker}...{Style.RESET_ALL}")
        try:
            stock_data = fetch_stock_data(ticker)
            if stock_data:
                stocks_data.append(stock_data)
                print(f"{Fore.GREEN}✓ {ticker} data retrieved{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Unable to fetch data for {ticker}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error fetching {ticker}: {str(e)}{Style.RESET_ALL}")
    
    if len(stocks_data) < 2:
        print(f"\n{Fore.RED}❌ Could not fetch data for enough stocks to compare{Style.RESET_ALL}")
        return
    
    # Display comparison
    print(f"\n{Fore.GREEN}✓ Successfully fetched data for {len(stocks_data)} stock(s){Style.RESET_ALL}")
    display.display_comparison_table(stocks_data)



def view_saved_reports_flow() -> None:
    """Display and allow selection of saved reports"""
    print(f"\n{Fore.CYAN}=== Saved Reports ==={Style.RESET_ALL}\n")
    
    reports = utils.list_saved_reports()
    
    if not reports:
        print(f"{Fore.YELLOW}No saved reports found.{Style.RESET_ALL}")
        return
    
    # Display list of reports
    print(f"Found {len(reports)} report(s):\n")
    for i, (filename, filepath, creation_date) in enumerate(reports, 1):
        date_str = creation_date.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {filename} (Created: {date_str})")
    
    # Get user selection
    try:
        choice = input(f"\n{Fore.CYAN}Enter report number to view (or 0 to go back): {Style.RESET_ALL}").strip()
        choice_num = int(choice)
        
        if choice_num == 0:
            return
        
        if 1 <= choice_num <= len(reports):
            filename, filepath, _ = reports[choice_num - 1]
            print(f"\n{Fore.CYAN}{'=' * 60}")
            print(f"Report: {filename}")
            print(f"{'=' * 60}{Style.RESET_ALL}\n")
            
            content = utils.load_report(filepath)
            print(content)
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Invalid selection{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error loading report: {str(e)}{Style.RESET_ALL}")



def display_help_flow() -> None:
    """Show comprehensive help documentation"""
    print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
    print(f"║           UNDERSTANDING FUNDAMENTAL DATA                   ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    help_content = """
📊 P/E RATIO (Price to Earnings):
What: Price you pay for each ₹1 of company earnings
Good: 15-25 (fairly valued)
Bad: >40 (expensive) or <10 (might indicate problems)

📊 ROE (Return on Equity):
What: How efficiently company uses shareholder money
Good: >15% (excellent)
Average: 10-15%
Bad: <10% or negative

📊 DEBT-TO-EQUITY:
What: How much debt vs equity company has
Good: <0.5 (low debt)
Average: 0.5-1.0
Bad: >2.0 (high debt, risky)

📊 PROFIT MARGIN:
What: Percentage of revenue that becomes profit
Good: >15% (healthy)
Average: 5-15%
Bad: <5% or negative

📊 P/B RATIO (Price to Book):
What: Stock price compared to book value per share
Good: <3 (reasonable)
Bad: Very high values may indicate overvaluation

📊 CURRENT RATIO:
What: Ability to pay short-term obligations
Good: >1.5 (strong liquidity)
Average: 1.0-1.5
Bad: <1.0 (liquidity concerns)

📊 EPS (Earnings Per Share):
What: Company's profit divided by number of shares
Good: Growing EPS over time
Bad: Declining or negative EPS

📊 REVENUE GROWTH:
What: Year-over-year increase in sales
Good: >10% (strong growth)
Average: 5-10%
Bad: Negative (declining sales)

📊 FREE CASH FLOW:
What: Cash generated after capital expenditures
Good: Positive and growing
Bad: Negative (burning cash)

📊 BETA:
What: Stock volatility compared to market
<1: Less volatile than market
>1: More volatile than market

═══════════════════════════════════════════════════════════════

POPULAR INDIAN STOCK SYMBOLS:

Large Cap:
• RELIANCE.NS - Reliance Industries
• TCS.NS - Tata Consultancy Services
• HDFCBANK.NS - HDFC Bank
• INFY.NS - Infosys
• HINDUNILVR.NS - Hindustan Unilever
• ITC.NS - ITC Limited
• BHARTIARTL.NS - Bharti Airtel
• SBIN.NS - State Bank of India

Mid Cap:
• ZOMATO.NS - Zomato
• NYKAA.NS - Nykaa
• DMART.NS - Avenue Supermarts

Note: Use .NS for NSE stocks and .BO for BSE stocks
"""
    
    print(help_content)
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")



def main():
    """Application entry point with main event loop"""
    # Display welcome banner
    print(f"\n{Fore.GREEN}{'=' * 60}")
    print(f"  Welcome to Stock Fundamental Analyzer")
    print(f"  Analyze Indian Stocks (NSE/BSE) with Confidence")
    print(f"{'=' * 60}{Style.RESET_ALL}\n")
    
    while True:
        display_main_menu()
        
        try:
            choice = input(f"{Fore.CYAN}Enter your choice (1-5): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                analyze_single_stock_flow()
            elif choice == '2':
                compare_stocks_flow()
            elif choice == '3':
                view_saved_reports_flow()
            elif choice == '4':
                display_help_flow()
            elif choice == '5':
                print(f"\n{Fore.GREEN}Thank you for using Stock Fundamental Analyzer!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Happy Investing! 📈{Style.RESET_ALL}\n")
                sys.exit(0)
            else:
                print(f"\n{Fore.RED}❌ Invalid choice. Please enter a number between 1 and 5.{Style.RESET_ALL}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrupted by user. Exiting...{Style.RESET_ALL}\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}❌ An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please try again.{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()



def build_report(stock_data, score, flags, chart_paths) -> str:
    """Build complete text report with all sections"""
    from datetime import datetime
    from analyzer import categorize_market_cap
    
    lines = []
    lines.append("=" * 70)
    lines.append("STOCK FUNDAMENTAL ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append(f"Stock: {stock_data.ticker}")
    lines.append(f"Company: {stock_data.company_name or 'N/A'}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    
    # Company Overview
    lines.append("COMPANY OVERVIEW")
    lines.append("-" * 70)
    if stock_data.sector:
        lines.append(f"Sector: {stock_data.sector}")
    if stock_data.industry:
        lines.append(f"Industry: {stock_data.industry}")
    if stock_data.market_cap:
        category = categorize_market_cap(stock_data.market_cap)
        lines.append(f"Market Cap: {utils.format_large_number(stock_data.market_cap)} ({category})")
    if stock_data.description:
        lines.append(f"\nBusiness: {utils.truncate_text(stock_data.description, 300)}")
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
    lines.append("")
    
    # Red Flags
    lines.append("RED FLAGS")
    lines.append("-" * 70)
    if flags.red_flags:
        for flag_name, description in flags.red_flags:
            lines.append(f"❌ {flag_name}: {description}")
    else:
        lines.append("✓ No major red flags detected")
    lines.append("")
    
    # Green Flags
    lines.append("GREEN FLAGS")
    lines.append("-" * 70)
    if flags.green_flags:
        for flag_name, description in flags.green_flags:
            lines.append(f"✓ {flag_name}: {description}")
    else:
        lines.append("No significant green flags detected")
    lines.append("")
    
    # Key Metrics
    lines.append("KEY FINANCIAL METRICS")
    lines.append("-" * 70)
    if stock_data.pe_ratio:
        lines.append(f"P/E Ratio: {stock_data.pe_ratio:.2f}")
    if stock_data.pb_ratio:
        lines.append(f"P/B Ratio: {stock_data.pb_ratio:.2f}")
    if stock_data.roe:
        roe_pct = stock_data.roe * 100 if abs(stock_data.roe) < 1 else stock_data.roe
        lines.append(f"ROE: {roe_pct:.2f}%")
    if stock_data.debt_to_equity:
        de_val = stock_data.debt_to_equity / 100 if stock_data.debt_to_equity > 10 else stock_data.debt_to_equity
        lines.append(f"Debt-to-Equity: {de_val:.2f}")
    if stock_data.net_margin:
        margin_pct = stock_data.net_margin * 100 if abs(stock_data.net_margin) < 1 else stock_data.net_margin
        lines.append(f"Net Profit Margin: {margin_pct:.2f}%")
    if stock_data.revenue_growth:
        growth_pct = stock_data.revenue_growth * 100 if abs(stock_data.revenue_growth) < 1 else stock_data.revenue_growth
        lines.append(f"Revenue Growth: {growth_pct:.2f}%")
    if stock_data.current_price:
        lines.append(f"Current Price: ₹{stock_data.current_price:.2f}")
    lines.append("")
    
    # Charts
    if chart_paths:
        lines.append("GENERATED CHARTS")
        lines.append("-" * 70)
        for path in chart_paths:
            lines.append(f"• {path}")
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


