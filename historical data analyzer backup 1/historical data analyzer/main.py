"""
Indian Stock Market Analysis Tool
Analyzes Indian stocks (NSE/BSE) using yfinance library
Author: Stock Analysis Tool
Date: 2025-10-21
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Configuration
OUTPUT_FOLDER = "stock_analysis_output"

def create_output_folder():
    """Create output folder if it doesn't exist"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"✓ Created output folder: {OUTPUT_FOLDER}")

def display_welcome_message():
    """Display welcome message and instructions"""
    print("=" * 70)
    print(" " * 15 + "INDIAN STOCK MARKET ANALYZER")
    print("=" * 70)
    print("\nThis tool analyzes Indian stocks from NSE and BSE exchanges.")
    # print("\nPopular Indian Stock Symbols:")
    # print("\nLarge Cap Stocks:")
    # print("  • RELIANCE.NS    - Reliance Industries")
    # print("  • TCS.NS         - Tata Consultancy Services")
    # print("  • HDFCBANK.NS    - HDFC Bank")
    # print("  • INFY.NS        - Infosys")
    # print("  • HINDUNILVR.NS  - Hindustan Unilever")
    # print("  • ITC.NS         - ITC Limited")
    # print("  • BHARTIARTL.NS  - Bharti Airtel")
    # print("\nMid Cap Stocks:")
    # print("  • ZOMATO.NS      - Zomato")
    # print("  • NYKAA.NS       - Nykaa")
    # print("\nNote: Use .NS for NSE stocks, .BO for BSE stocks")
    print("=" * 70 + "\n")

def fetch_stock_data(ticker, period="1mo"):
    """
    Fetch stock data from yfinance
    
    Args:
        ticker (str): Stock ticker symbol (e.g., RELIANCE.NS)
        period (str): Time period for data (default: 1mo)
    
    Returns:
        tuple: (stock_object, dataframe) or (None, None) if error
    """
    try:
        print(f"\n⏳ Fetching data for {ticker}...")
        
        # Download stock data
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        
        # Check if data is empty
        if data.empty:
            print(f"❌ No data available for {ticker} in the last month.")
            return None, None
        
        print(f"✓ Successfully fetched {len(data)} days of data")
        return stock, data
    
    except Exception as e:
        if "No data found" in str(e):
            print(f"❌ Stock symbol '{ticker}' not found. Please check and try again.")
        elif "ConnectionError" in str(type(e).__name__):
            print("❌ No internet connection. Please check your connection.")
        else:
            print(f"❌ Error fetching data: {str(e)}")
        return None, None

def calculate_statistics(data):
    """
    Calculate key statistics from stock data
    
    Args:
        data (DataFrame): Stock price data
    
    Returns:
        dict: Dictionary containing calculated statistics
    """
    stats = {}
    
    # Current price (most recent close)
    stats['current_price'] = data['Close'].iloc[-1]
    
    # Month high and low
    stats['month_high'] = data['High'].max()
    stats['month_low'] = data['Low'].min()
    
    # Average daily volume
    stats['avg_volume'] = data['Volume'].mean()
    
    # Total percentage change
    first_price = data['Close'].iloc[0]
    last_price = data['Close'].iloc[-1]
    stats['total_change_pct'] = ((last_price - first_price) / first_price) * 100
    
    # Calculate daily returns
    data['Daily_Return'] = data['Close'].pct_change() * 100
    
    # Best and worst day
    best_day_idx = data['Daily_Return'].idxmax()
    worst_day_idx = data['Daily_Return'].idxmin()
    
    stats['best_day'] = {
        'date': best_day_idx.strftime('%Y-%m-%d') if pd.notna(best_day_idx) else 'N/A',
        'return': data['Daily_Return'].max()
    }
    
    stats['worst_day'] = {
        'date': worst_day_idx.strftime('%Y-%m-%d') if pd.notna(worst_day_idx) else 'N/A',
        'return': data['Daily_Return'].min()
    }
    
    # Volatility (standard deviation of returns)
    stats['volatility'] = data['Daily_Return'].std()
    
    # Average daily return
    stats['avg_daily_return'] = data['Daily_Return'].mean()
    
    # Trading days
    stats['trading_days'] = len(data)
    
    # Calculate moving averages
    data['SMA_7'] = data['Close'].rolling(window=7).mean()
    data['SMA_14'] = data['Close'].rolling(window=14).mean()
    
    # Last updated
    stats['last_updated'] = data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
    
    return stats, data

def display_statistics(ticker, stats, stock):
    """
    Display key statistics in a formatted manner
    
    Args:
        ticker (str): Stock ticker symbol
        stats (dict): Dictionary of calculated statistics
        stock (yfinance.Ticker): Stock object
    """
    print("\n" + "=" * 70)
    print(f" " * 20 + f"ANALYSIS FOR {ticker}")
    print("=" * 70)
    
    # Try to get company name
    try:
        info = stock.info
        company_name = info.get('longName', ticker)
        print(f"\nCompany: {company_name}")
    except:
        print(f"\nStock: {ticker}")
    
    print(f"\n📊 KEY STATISTICS (Last {stats['trading_days']} Trading Days)")
    print("-" * 70)
    print(f"Current Price:           ₹{stats['current_price']:.2f}")
    print(f"Month High:              ₹{stats['month_high']:.2f}")
    print(f"Month Low:               ₹{stats['month_low']:.2f}")
    print(f"Total Change:            {stats['total_change_pct']:+.2f}%")
    print(f"Average Daily Volume:    {stats['avg_volume']:,.0f}")
    print(f"Average Daily Return:    {stats['avg_daily_return']:.2f}%")
    print(f"Volatility (Std Dev):    {stats['volatility']:.2f}%")
    
    print(f"\n📈 BEST & WORST DAYS")
    print("-" * 70)
    print(f"Best Day:   {stats['best_day']['date']}  ({stats['best_day']['return']:+.2f}%)")
    print(f"Worst Day:  {stats['worst_day']['date']}  ({stats['worst_day']['return']:+.2f}%)")
    
    print(f"\n🕐 Last Updated: {stats['last_updated']}")
    print("=" * 70)

def display_summary_table(data, ticker):
    """
    Display a formatted table of stock data
    
    Args:
        data (DataFrame): Stock price data with calculated fields
        ticker (str): Stock ticker symbol
    """
    print(f"\n📋 DETAILED DATA TABLE FOR {ticker}")
    print("=" * 100)
    
    # Create a copy for display
    display_data = data[['Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return']].copy()
    
    # Format the data
    display_data['Date'] = display_data.index.strftime('%Y-%m-%d')
    display_data = display_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return']]
    
    # Print header
    print(f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>15} {'Change %':>10}")
    print("-" * 100)
    
    # Print rows
    for idx, row in display_data.iterrows():
        date_str = row['Date']
        open_val = f"₹{row['Open']:.2f}"
        high_val = f"₹{row['High']:.2f}"
        low_val = f"₹{row['Low']:.2f}"
        close_val = f"₹{row['Close']:.2f}"
        volume_val = f"{row['Volume']:,.0f}"
        change_val = f"{row['Daily_Return']:+.2f}%" if pd.notna(row['Daily_Return']) else "N/A"
        
        print(f"{date_str:<12} {open_val:>10} {high_val:>10} {low_val:>10} {close_val:>10} {volume_val:>15} {change_val:>10}")
    
    print("=" * 100)

def create_price_chart(data, ticker):
    """
    Create line chart showing closing prices
    
    Args:
        data (DataFrame): Stock price data
        ticker (str): Stock ticker symbol
    
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot closing price
    ax.plot(data.index, data['Close'], label='Close Price', color='#1f77b4', linewidth=2)
    
    # Formatting
    ax.set_title(f'{ticker} - 30 Day Price Analysis', loc='left', fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Price (₹)', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Move y-axis to right side
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def create_candlestick_chart(data, ticker):
    """
    Create candlestick chart showing OHLC data
    
    Args:
        data (DataFrame): Stock price data
        ticker (str): Stock ticker symbol
    
    Returns:
        str: Path to saved candlestick chart
    """
    # Define style
    mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', edge='inherit', wick='inherit', volume='in')
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', gridcolor='#e0e0e0', facecolor='white')
    
    # Create filename
    timestamp = datetime.now().strftime('%Y_%m_%d')
    filename = f"{OUTPUT_FOLDER}/{ticker.replace('.', '_')}_candlestick_{timestamp}.png"
    
    # Create figure and axes
    fig, axes = mpf.plot(data, type='candle', style=s, volume=True, 
                         ylabel='Price (₹)', ylabel_lower='Volume',
                         figsize=(12, 8), returnfig=True)
    
    # Move y-axis to right side for both price and volume panels
    axes[0].yaxis.tick_right()
    axes[0].yaxis.set_label_position("right")
    axes[2].yaxis.tick_right()
    axes[2].yaxis.set_label_position("right")
    
    # Add title at top-left
    fig.suptitle(f'{ticker} - Candlestick Chart (30 Days)', 
                 x=0.125, y=0.98, ha='left', fontsize=12, fontweight='bold')
    
    # Save the figure
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return filename

def create_volume_chart(data, ticker):
    """
    Create bar chart showing trading volume
    
    Args:
        data (DataFrame): Stock price data
        ticker (str): Stock ticker symbol
    
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create color array (green for up days, red for down days)
    colors = ['#26a69a' if close >= open_price else '#ef5350' 
              for close, open_price in zip(data['Close'], data['Open'])]
    
    # Plot volume bars
    ax.bar(data.index, data['Volume'], color=colors, alpha=0.7, width=0.8)
    
    # Formatting
    ax.set_title(f'{ticker} - Trading Volume (30 Days)', loc='left', fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Volume', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Format y-axis to show numbers in readable format
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    
    # Move y-axis to right side
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def save_charts(ticker, price_fig, volume_fig):
    """
    Save all charts to files
    
    Args:
        ticker (str): Stock ticker symbol
        price_fig (Figure): Price chart figure
        volume_fig (Figure): Volume chart figure
    
    Returns:
        list: List of saved file paths
    """
    saved_files = []
    timestamp = datetime.now().strftime('%Y_%m_%d')
    ticker_clean = ticker.replace('.', '_')
    
    try:
        # Save price chart
        price_filename = f"{OUTPUT_FOLDER}/{ticker_clean}_price_{timestamp}.png"
        price_fig.savefig(price_filename, dpi=300, bbox_inches='tight')
        saved_files.append(price_filename)
        print(f"✓ Saved price chart: {price_filename}")
        
        # Save volume chart
        volume_filename = f"{OUTPUT_FOLDER}/{ticker_clean}_volume_{timestamp}.png"
        volume_fig.savefig(volume_filename, dpi=300, bbox_inches='tight')
        saved_files.append(volume_filename)
        print(f"✓ Saved volume chart: {volume_filename}")
        
        # Close figures to free memory
        plt.close(price_fig)
        plt.close(volume_fig)
        
    except Exception as e:
        print(f"❌ Error saving charts: {str(e)}")
    
    return saved_files

def export_to_txt(data, ticker):
    """
    Export stock data to TXT file
    
    Args:
        data (DataFrame): Stock price data
        ticker (str): Stock ticker symbol
    """
    try:
        timestamp = datetime.now().strftime('%Y_%m_%d')
        ticker_clean = ticker.replace('.', '_')
        filename = f"{OUTPUT_FOLDER}/{ticker_clean}_data_{timestamp}.txt"
        
        # Select columns to export
        export_data = data[['Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return', 'SMA_7', 'SMA_14']].copy()
        
        # Save as tab-separated TXT file
        export_data.to_csv(filename, sep='\t')
        
        print(f"✓ Exported data to TXT: {filename}")
        return filename
    
    except Exception as e:
        print(f"❌ Error exporting to TXT: {str(e)}")
        return None

def analyze_stock(ticker):
    """
    Main function to analyze a single stock
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        bool: True if analysis successful, False otherwise
    """
    # Fetch stock data
    stock, data = fetch_stock_data(ticker)
    
    if stock is None or data is None:
        return False
    
    # Calculate statistics
    stats, data = calculate_statistics(data)
    
    # Display statistics
    display_statistics(ticker, stats, stock)
    
    # Display data table
    display_summary_table(data, ticker)
    
    # Create charts
    print(f"\n📊 Generating charts for {ticker}...")
    
    try:
        # Create price chart
        price_fig = create_price_chart(data, ticker)
        
        # Create volume chart
        volume_fig = create_volume_chart(data, ticker)
        
        # Create candlestick chart
        candlestick_file = create_candlestick_chart(data, ticker)
        print(f"✓ Saved candlestick chart: {candlestick_file}")
        
        # Save other charts
        saved_files = save_charts(ticker, price_fig, volume_fig)
        
        # Export to TXT
        txt_file = export_to_txt(data, ticker)
        
        print(f"\n✅ Analysis complete! All files saved to '{OUTPUT_FOLDER}' folder.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating charts: {str(e)}")
        return False

def get_user_input():
    """
    Get stock ticker from user with validation
    
    Returns:
        str: Stock ticker symbol or None to exit
    """
    while True:
        ticker = input("\nEnter stock ticker symbol (or 'quit' to exit): ").strip().upper()
        
        if ticker.lower() in ['quit', 'exit', 'q']:
            return None
        
        if not ticker:
            print("❌ Please enter a valid ticker symbol.")
            continue
        
        # Add .NS if no exchange suffix provided
        if '.' not in ticker:
            print(f"ℹ️  No exchange specified. Assuming NSE (.NS)")
            ticker = ticker + '.NS'
        
        return ticker

def main():
    """
    Main program loop
    """
    # Create output folder
    create_output_folder()
    
    # Display welcome message
    display_welcome_message()
    
    # Main loop for multiple stock analysis
    while True:
        # Get user input
        ticker = get_user_input()
        
        if ticker is None:
            print("\n👋 Thank you for using Indian Stock Market Analyzer!")
            print("=" * 70)
            break
        
        # Analyze the stock
        success = analyze_stock(ticker)
        
        # Ask if user wants to analyze another stock
        if success:
            print("\n" + "-" * 70)
            continue_analysis = input("\nWould you like to analyze another stock? (yes/no): ").strip().lower()
            
            if continue_analysis not in ['yes', 'y']:
                print("\n👋 Thank you for using Indian Stock Market Analyzer!")
                print("=" * 70)
                break
        else:
            # If analysis failed, ask if they want to try again
            retry = input("\nWould you like to try another stock? (yes/no): ").strip().lower()
            
            if retry not in ['yes', 'y']:
                print("\n👋 Thank you for using Indian Stock Market Analyzer!")
                print("=" * 70)
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user.")
        print("👋 Thank you for using Indian Stock Market Analyzer!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
