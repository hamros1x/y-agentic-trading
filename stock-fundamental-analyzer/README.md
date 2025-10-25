# Stock Fundamental Analyzer

A professional-grade Python application for comprehensive fundamental analysis of Indian stocks listed on NSE/BSE exchanges.

## Features

- **Company Overview**: Detailed company information including sector, industry, market cap, and business description
- **Financial Metrics**: Complete analysis of valuation ratios, profitability metrics, financial health, and growth indicators
- **Investment Scoring**: Automated 0-100 investment quality score based on key fundamentals
- **Red/Green Flags**: Automatic detection of warning signs and positive indicators
- **Financial Statements**: Display of income statement, balance sheet, and cash flow data
- **Visual Charts**: Generate trend charts for revenue, profit, EPS, and more
- **Multi-Stock Comparison**: Compare 2-5 stocks side-by-side
- **Report Generation**: Save detailed analysis reports for future reference
- **Analyst Data**: View analyst recommendations and target prices

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection (for fetching stock data)

### Setup

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Main Menu Options

1. **Analyze Single Stock**: Comprehensive analysis of a single stock
2. **Compare Multiple Stocks**: Side-by-side comparison of 2-5 stocks
3. **View Saved Reports**: Access previously saved analysis reports
4. **Help**: Learn how to interpret fundamental data
5. **Exit**: Close the application

### Stock Symbol Format

- NSE stocks: Use `.NS` suffix (e.g., `RELIANCE.NS`)
- BSE stocks: Use `.BO` suffix (e.g., `RELIANCE.BO`)

### Popular Indian Stock Symbols

**Large Cap:**
- RELIANCE.NS - Reliance Industries
- TCS.NS - Tata Consultancy Services
- HDFCBANK.NS - HDFC Bank
- INFY.NS - Infosys
- HINDUNILVR.NS - Hindustan Unilever
- ITC.NS - ITC Limited
- BHARTIARTL.NS - Bharti Airtel
- SBIN.NS - State Bank of India

**Mid Cap:**
- ZOMATO.NS - Zomato
- NYKAA.NS - Nykaa
- DMART.NS - Avenue Supermarts

## Understanding Fundamental Data

### Key Metrics Explained

**P/E Ratio (Price to Earnings)**
- What it means: Price you pay for each ₹1 of earnings
- Good: 15-25 (fairly valued)
- Concerning: >40 (expensive) or <10 (potential issues)

**ROE (Return on Equity)**
- What it means: How efficiently company uses shareholder capital
- Excellent: >15%
- Average: 10-15%
- Poor: <10% or negative

**Debt-to-Equity Ratio**
- What it means: Company's leverage level
- Good: <0.5 (low debt)
- Average: 0.5-1.0
- Risky: >2.0 (high debt)

**Profit Margin**
- What it means: Percentage of revenue that becomes profit
- Healthy: >15%
- Moderate: 5-15%
- Concerning: <5% or negative

**Revenue Growth**
- What it means: Year-over-year sales increase
- Strong: >10%
- Moderate: 5-10%
- Concerning: Negative (declining)

## Investment Quality Score

The application calculates a 0-100 score based on:
- P/E Ratio (30 points max)
- ROE (20 points max)
- Debt-to-Equity (20 points max)
- Profit Margin (15 points max)
- Revenue Growth (15 points max)

**Score Interpretation:**
- 80-100: Excellent fundamentals
- 60-79: Good fundamentals
- 40-59: Average fundamentals
- 20-39: Weak fundamentals
- 0-19: Poor fundamentals

## Red Flags (Warning Signs)

The system automatically detects:
- High debt (D/E > 2.0)
- Negative ROE
- Declining revenue
- Negative profit margins
- Very high P/E (>50)
- Negative cash flow

## Green Flags (Positive Signs)

The system automatically detects:
- Strong ROE (>15%)
- Low debt (D/E < 0.5)
- Strong revenue growth (>10%)
- Healthy profit margins (>15%)
- Positive free cash flow
- Reasonable P/E (10-25)

## Output Files

### Reports
- Location: `fundamental_reports/`
- Format: `{TICKER}_{TIMESTAMP}.txt`
- Contains: Complete analysis with all metrics and interpretations

### Charts
- Location: `charts/{TICKER}/`
- Format: PNG images
- Types: Revenue trend, profit trend, EPS trend, debt vs equity, margin trend

### Logs
- Location: `stock_analyzer.log`
- Contains: Error logs for debugging

## Troubleshooting

### "Stock not found" Error
- Verify the stock symbol is correct
- Ensure you're using the right suffix (.NS for NSE, .BO for BSE)
- Check your internet connection
- Try again later if the service is busy

### Missing Data
- Some stocks may not have all metrics available
- The application will display "N/A" for unavailable data
- Charts require sufficient historical data (minimum 2 years)

### Slow Performance
- First-time data fetch may take 5-10 seconds
- Network speed affects performance
- Multiple stock comparison takes longer

## Limitations

- Data is fetched from Yahoo Finance via yfinance library
- Some stocks may have incomplete fundamental data
- Historical data availability varies by stock
- Peer comparison feature requires manual peer selection
- Real-time data may have slight delays

## Disclaimer

This tool is for informational and educational purposes only. It should not be considered as investment advice. Always consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.

## Dependencies

- yfinance: Stock data fetching
- pandas: Data manipulation
- matplotlib: Chart generation
- numpy: Numerical operations
- colorama: Colored terminal output

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check the Help section in the application
2. Review this README
3. Check the troubleshooting section
4. Verify your Python and dependency versions

## Version

Current Version: 1.0

---

**Happy Investing! 📈**
