# 📈 Indian Stock Market Analyzer

A comprehensive Python tool for analyzing Indian stocks from NSE (National Stock Exchange) and BSE (Bombay Stock Exchange) using real-time data from Yahoo Finance.

## 🌟 Features

- **Real-time Data Fetching**: Downloads last 30 days of stock data using yfinance
- **Comprehensive Analysis**: 
  - Price trends with moving averages (7-day and 14-day SMA)
  - Candlestick charts for OHLC (Open, High, Low, Close) visualization
  - Volume analysis with color-coded bars
  - Key statistics including volatility, best/worst days, and returns
- **Beautiful Visualizations**: Professional charts with proper formatting
- **Data Export**: Saves all charts as PNG files and exports data to CSV
- **Multiple Stock Analysis**: Analyze as many stocks as you want in one session
- **Error Handling**: Robust error handling for invalid tickers and network issues

## 📋 Requirements

- Python 3.8 or higher
- Internet connection for fetching stock data

## 🚀 Installation

### Step 1: Clone or Download

Download the project files to your local machine.

### Step 2: Install Python Dependencies

Open your terminal/command prompt and navigate to the project directory, then run:

```bash
pip install -r requirements.txt
```

This will install all required libraries:
- `yfinance` - For fetching stock data from Yahoo Finance
- `pandas` - For data manipulation and analysis
- `matplotlib` - For creating charts and graphs
- `mplfinance` - For candlestick charts
- `numpy` - For numerical calculations

### Alternative Installation (Individual Packages)

If you prefer to install packages individually:

```bash
pip install yfinance pandas matplotlib mplfinance numpy
```

## 💻 How to Run

1. Open terminal/command prompt
2. Navigate to the project directory
3. Run the program:

```bash
python main.py
```

4. Follow the on-screen prompts to enter stock ticker symbols

## 📊 Example Stock Symbols

### Large Cap Stocks (NSE)
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `HDFCBANK.NS` - HDFC Bank
- `INFY.NS` - Infosys
- `HINDUNILVR.NS` - Hindustan Unilever
- `ITC.NS` - ITC Limited
- `BHARTIARTL.NS` - Bharti Airtel

### Mid Cap Stocks (NSE)
- `ZOMATO.NS` - Zomato
- `NYKAA.NS` - Nykaa

### BSE Stocks
- `RELIANCE.BO` - Reliance Industries (BSE)
- `TCS.BO` - Tata Consultancy Services (BSE)

**Note**: 
- Use `.NS` suffix for NSE (National Stock Exchange) stocks
- Use `.BO` suffix for BSE (Bombay Stock Exchange) stocks
- If you don't specify an exchange, the program assumes NSE (.NS)

## 📁 Output Files

All generated files are saved in the `stock_analysis_output` folder:

1. **Price Chart** (`TICKER_price_YYYY_MM_DD.png`)
   - Line chart showing closing prices
   - 7-day and 14-day moving averages
   
2. **Candlestick Chart** (`TICKER_candlestick_YYYY_MM_DD.png`)
   - OHLC candlestick visualization
   - Volume bars at the bottom
   
3. **Volume Chart** (`TICKER_volume_YYYY_MM_DD.png`)
   - Trading volume bars
   - Color-coded (green for up days, red for down days)
   
4. **CSV Data** (`TICKER_data_YYYY_MM_DD.csv`)
   - Complete data export with all calculated fields

## 📖 Usage Example

```
Enter stock ticker symbol (or 'quit' to exit): RELIANCE.NS

⏳ Fetching data for RELIANCE.NS...
✓ Successfully fetched 21 days of data

======================================================================
                    ANALYSIS FOR RELIANCE.NS
======================================================================

Company: Reliance Industries Limited

📊 KEY STATISTICS (Last 21 Trading Days)
----------------------------------------------------------------------
Current Price:           ₹2,456.30
Month High:              ₹2,498.75
Month Low:               ₹2,401.20
Total Change:            +2.15%
Average Daily Volume:    8,456,234
Average Daily Return:    0.12%
Volatility (Std Dev):    1.23%

📈 BEST & WORST DAYS
----------------------------------------------------------------------
Best Day:   2025-10-15  (+3.45%)
Worst Day:  2025-10-08  (-2.12%)

[... detailed data table ...]

📊 Generating charts for RELIANCE.NS...
✓ Saved candlestick chart: stock_analysis_output/RELIANCE_NS_candlestick_2025_10_21.png
✓ Saved price chart: stock_analysis_output/RELIANCE_NS_price_2025_10_21.png
✓ Saved volume chart: stock_analysis_output/RELIANCE_NS_volume_2025_10_21.png
✓ Exported data to CSV: stock_analysis_output/RELIANCE_NS_data_2025_10_21.csv

✅ Analysis complete! All files saved to 'stock_analysis_output' folder.
```

## 🔧 Troubleshooting

### Issue: "Stock symbol not found"
**Solution**: 
- Verify the ticker symbol is correct
- Ensure you're using the right exchange suffix (.NS or .BO)
- Check if the stock is actively traded

### Issue: "No internet connection"
**Solution**: 
- Check your internet connection
- Verify you can access yahoo.com
- Try again after a few moments

### Issue: "No data available for this stock"
**Solution**: 
- The stock might be newly listed
- Try a different time period
- Verify the stock is actively traded

### Issue: "Module not found" error
**Solution**: 
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Charts not displaying properly
**Solution**: 
- Ensure matplotlib is properly installed
- Check if the output folder has write permissions
- Try running with administrator/sudo privileges

### Issue: "Permission denied" when saving files
**Solution**: 
- Run the program from a directory where you have write permissions
- On Windows: Run command prompt as administrator
- On Mac/Linux: Check folder permissions with `ls -la`

## 🎯 Key Statistics Explained

- **Current Price**: Most recent closing price
- **Month High/Low**: Highest and lowest prices in the period
- **Total Change**: Percentage change from first to last day
- **Average Daily Volume**: Mean trading volume per day
- **Average Daily Return**: Mean percentage change per day
- **Volatility**: Standard deviation of daily returns (higher = more volatile)
- **Best/Worst Day**: Days with highest gain and loss

## 🛠️ Technical Indicators

- **7-Day SMA**: Simple Moving Average over 7 days (short-term trend)
- **14-Day SMA**: Simple Moving Average over 14 days (medium-term trend)
- **Daily Returns**: Percentage change from previous day
- **Volume Analysis**: Trading activity patterns

## 📸 Expected Output

After running the analysis, you should see:

1. **Console Output**: 
   - Welcome message with stock examples
   - Real-time fetching status
   - Comprehensive statistics
   - Detailed data table
   - File save confirmations

2. **Generated Charts**:
   - Professional-looking price chart with moving averages
   - Candlestick chart with volume bars
   - Volume bar chart with color coding

3. **CSV File**:
   - Complete data export for further analysis in Excel or other tools

## 🔒 Privacy & Security

- This tool only fetches publicly available stock market data
- No personal information is collected or stored
- All data is processed locally on your machine
- No data is sent to any third-party servers (except Yahoo Finance for stock data)

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It should not be considered as financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## 📝 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📧 Support

If you encounter any issues or have questions, please check the troubleshooting section above.

---

**Happy Analyzing! 📈💹**
