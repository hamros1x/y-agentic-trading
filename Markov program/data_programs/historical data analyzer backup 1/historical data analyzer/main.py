"""
15-Minute Intraday Data Fetcher for Markov Prediction System
Fetches 15-minute candle data and saves to output_data/historical_data.txt
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

TXT_OUTPUT_FOLDER = "output_data"

def create_output_folder():
    """Create output folder if it doesn't exist"""
    if not os.path.exists(TXT_OUTPUT_FOLDER):
        os.makedirs(TXT_OUTPUT_FOLDER)

def display_welcome_message():
    """Display welcome message"""
    print("=" * 70)
    print(" " * 10 + "15-MINUTE INTRADAY DATA FETCHER")
    print("=" * 70)
    print("\nFetches 15-minute candle data for Markov prediction system.")
    print("=" * 70 + "\n")

def fetch_stock_data(ticker, days_back):
    """Fetch 15-minute intraday stock data from yfinance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        print(f"\n⏳ Fetching 15-minute data for {days_back} days...")
        print(f"   From: {start_date.strftime('%Y-%m-%d')}")
        print(f"   To:   {end_date.strftime('%Y-%m-%d')}")
        
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, interval="15m")
        
        if data.empty:
            print(f"❌ No data available for {ticker}")
            return None
        
        print(f"✓ Successfully fetched {len(data)} candles")
        return data
    
    except Exception as e:
        if "No data found" in str(e):
            print(f"❌ Stock symbol '{ticker}' not found")
        elif "ConnectionError" in str(type(e).__name__):
            print("❌ No internet connection")
        else:
            print(f"❌ Error: {str(e)}")
        return None

def save_to_file(data):
    """Save data to standardized output file"""
    try:
        output_path = f'{TXT_OUTPUT_FOLDER}/historical_data.txt'
        
        data['Daily_Return'] = data['Close'].pct_change() * 100
        export_data = data[['Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return']].copy()
        export_data.to_csv(output_path, sep='\t')
        
        print(f"\n✓ Data saved to: {output_path}")
        print(f"✓ Total candles: {len(data)}")
        print(f"✓ Date range: {data.index[0].date()} to {data.index[-1].date()}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error saving file: {str(e)}")
        return False

def get_days_back():
    """Get number of days for historical data"""
    print("\n📅 DATA RANGE SELECTION")
    print("-" * 70)
    print("Recommended: 60 days (provides ~2 months of 15-min data)")
    print("Examples:")
    print("  • 30 for 1 month")
    print("  • 60 for 2 months")
    print("  • 90 for 3 months")
    print("-" * 70)
    
    while True:
        user_input = input("\nHow many days of data? (minimum 7, or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            return None
        
        try:
            days_back = int(user_input)
            
            if days_back < 7:
                print("❌ Minimum 7 days required")
                continue
            
            print(f"✓ Selected: {days_back} days")
            return days_back
            
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def get_ticker():
    """Get stock ticker from user"""
    while True:
        ticker = input("\nEnter stock ticker symbol (or 'quit' to exit): ").strip().upper()
        
        if ticker.lower() in ['quit', 'exit', 'q']:
            return None
        
        if not ticker:
            print("❌ Please enter a valid ticker symbol")
            continue
        
        if '.' not in ticker:
            print(f"ℹ️  No exchange specified. Assuming NSE (.NS)")
            ticker = ticker + '.NS'
        
        return ticker

def main():
    """Main program"""
    create_output_folder()
    display_welcome_message()
    
    while True:
        ticker = get_ticker()
        
        if ticker is None:
            print("\n👋 Exiting program")
            print("=" * 70)
            break
        
        days_back = get_days_back()
        
        if days_back is None:
            print("\n👋 Exiting program")
            print("=" * 70)
            break
        
        data = fetch_stock_data(ticker, days_back)
        
        if data is not None:
            success = save_to_file(data)
            
            if success:
                print("\n" + "=" * 70)
                print("✅ DATA FETCH COMPLETE")
                print("=" * 70)
                print("\nYou can now run the Markov prediction system:")
                print("  python strategy_files/markov_trading_system.py")
                print("\n" + "-" * 70)
                
                continue_fetch = input("\nFetch data for another stock? (yes/no): ").strip().lower()
                
                if continue_fetch not in ['yes', 'y']:
                    print("\n👋 Thank you!")
                    print("=" * 70)
                    break
        else:
            retry = input("\nTry another stock? (yes/no): ").strip().lower()
            
            if retry not in ['yes', 'y']:
                print("\n👋 Thank you!")
                print("=" * 70)
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
