"""
Historical Stock Data Downloader
Downloads daily and 15-minute interval data for Indian stocks (NSE/BSE)
"""

import yfinance as yf
import pandas as pd
import os
import sys

DATA_FOLDER = "data"

def create_data_folder():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

def download_daily(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1y", interval="1d")
        
        if data.empty:
            return None
        
        return data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
    except:
        return None

def download_intraday(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="60d", interval="15m")
        
        if data.empty:
            return None
        
        return data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
    except:
        return None

def save_csv(data, filename):
    filepath = os.path.join(DATA_FOLDER, filename)
    data.to_csv(filepath)
    return filepath

def main():
    print("=" * 70)
    print(" " * 15 + "HISTORICAL STOCK DATA DOWNLOADER")
    print("=" * 70)
    print("\nDownloads 1 year daily data + 60 days 15-minute data")
    print("Note: Use .NS for NSE stocks, .BO for BSE stocks")
    print("=" * 70 + "\n")
    
    create_data_folder()
    
    ticker = input("Enter stock ticker (e.g., RELIANCE.NS for NSE, TATASTEEL.BO for BSE): ").strip().upper()
    
    if not ticker:
        print("Error: Invalid ticker")
        sys.exit(1)
    
    if '.' not in ticker:
        ticker = ticker + '.NS'
        print(f"No exchange specified. Using {ticker}")
    
    print("\nDownloading daily data...")
    daily_data = download_daily(ticker)
    
    if daily_data is None:
        print(f"Error: Could not download data for {ticker}")
        print("Please check ticker symbol and internet connection")
        sys.exit(1)
    
    print("Downloading 15-min data...")
    intraday_data = download_intraday(ticker)
    
    if intraday_data is None:
        print(f"Error: Could not download 15-min data for {ticker}")
        sys.exit(1)
    
    daily_file = save_csv(daily_data, f"{ticker}_daily.csv")
    intraday_file = save_csv(intraday_data, f"{ticker}_15min.csv")
    
    print("\nDone! Files saved:")
    print(f"- {daily_file}")
    print(f"- {intraday_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
