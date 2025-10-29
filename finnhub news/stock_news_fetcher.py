import finnhub
import json
from datetime import datetime, timedelta
import time
import sys

def print_separator():
    print("\n" + "="*80 + "\n")

def get_stock_symbol(stock_name):
    """Convert stock name to NSE/BSE symbol format"""
    stock_upper = stock_name.upper().strip()
    
    # Remove common suffixes if present
    stock_upper = stock_upper.replace('.NS', '').replace('.BO', '')
    
    # Try NSE first (more liquid market)
    nse_symbol = f"{stock_upper}.NS"
    bse_symbol = f"{stock_upper}.BO"
    
    return nse_symbol, bse_symbol

def fetch_company_news(api_client, symbol, from_date, to_date):
    """Fetch company news from Finnhub"""
    try:
        # Remove exchange suffix for API call
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        news = api_client.company_news(clean_symbol, _from=from_date, to=to_date)
        return news
    except Exception as e:
        return None

def format_news_article(article, index):
    """Format a single news article for display"""
    output = []
    output.append(f"\n{'─'*80}")
    output.append(f"NEWS ARTICLE #{index}")
    output.append(f"{'─'*80}\n")
    
    output.append(f"HEADLINE: {article.get('headline', 'N/A')}\n")
    
    # Format date
    timestamp = article.get('datetime', 0)
    if timestamp:
        date_str = datetime.fromtimestamp(timestamp).strftime('%d %B %Y, %I:%M %p IST')
        output.append(f"DATE: {date_str}\n")
    
    output.append(f"SOURCE: {article.get('source', 'N/A')}\n")
    output.append(f"CATEGORY: {article.get('category', 'N/A')}\n")
    
    summary = article.get('summary', 'N/A')
    output.append(f"\nCONTENT:\n{summary}\n")
    
    url = article.get('url', '')
    if url:
        output.append(f"\nREAD FULL ARTICLE: {url}\n")
    
    related = article.get('related', '')
    if related:
        output.append(f"RELATED STOCKS: {related}\n")
    
    return '\n'.join(output)

def save_to_file(content, filename):
    """Save content to text file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def main():
    print_separator()
    print("🔴 INDIAN STOCK NEWS FETCHER (NSE/BSE) 🔴")
    print("Powered by Finnhub API")
    print_separator()
    
    # Get API key
    print("Please enter your Finnhub API key:")
    print("(Get free API key from: https://finnhub.io/register)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("\n❌ API key is required! Please get a free key from https://finnhub.io/register")
        sys.exit(1)
    
    # Initialize Finnhub client
    try:
        finnhub_client = finnhub.Client(api_key=api_key)
        print("\n✅ API key validated successfully!")
    except Exception as e:
        print(f"\n❌ Error initializing Finnhub client: {e}")
        sys.exit(1)
    
    print_separator()
    
    # Get stock name
    print("Enter the stock symbol (e.g., RELIANCE, TCS, INFY, HDFCBANK):")
    stock_name = input("Stock Symbol: ").strip()
    
    if not stock_name:
        print("\n❌ Stock symbol cannot be empty!")
        sys.exit(1)
    
    print_separator()
    
    # Get number of days
    print("Enter number of days for news (1-365):")
    print("Note: Finnhub API may have limitations on historical data")
    try:
        days = int(input("Days: ").strip())
        if days < 1 or days > 365:
            print("\n❌ Please enter a value between 1 and 365")
            sys.exit(1)
    except ValueError:
        print("\n❌ Please enter a valid number!")
        sys.exit(1)
    
    print_separator()
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    to_date_str = to_date.strftime('%Y-%m-%d')
    from_date_str = from_date.strftime('%Y-%m-%d')
    
    print(f"📅 Fetching news from {from_date_str} to {to_date_str}")
    print(f"🔍 Searching for stock: {stock_name.upper()}")
    print("\n⏳ Please wait, fetching news from Finnhub...\n")
    
    # Get symbol formats
    nse_symbol, bse_symbol = get_stock_symbol(stock_name)
    
    # Try fetching from both NSE and BSE
    all_news = []
    
    # Try NSE first
    print(f"Checking NSE: {nse_symbol}...")
    nse_news = fetch_company_news(finnhub_client, nse_symbol, from_date_str, to_date_str)
    if nse_news:
        all_news.extend(nse_news)
        print(f"✅ Found {len(nse_news)} news articles from NSE")
    else:
        print("⚠️  No news found from NSE")
    
    time.sleep(1)  # Rate limiting
    
    # Try BSE
    print(f"Checking BSE: {bse_symbol}...")
    bse_news = fetch_company_news(finnhub_client, bse_symbol, from_date_str, to_date_str)
    if bse_news:
        # Avoid duplicates by checking headlines
        existing_headlines = {article.get('headline') for article in all_news}
        new_articles = [article for article in bse_news if article.get('headline') not in existing_headlines]
        all_news.extend(new_articles)
        print(f"✅ Found {len(new_articles)} unique news articles from BSE")
    else:
        print("⚠️  No news found from BSE")
    
    print_separator()
    
    # Process and display results
    if not all_news:
        print(f"❌ No news found for {stock_name.upper()} in the last {days} days")
        print("\nPossible reasons:")
        print("1. Stock symbol might be incorrect")
        print("2. No news coverage for this stock in Finnhub")
        print("3. API rate limit reached")
        print("\nPlease verify the stock symbol and try again.")
        sys.exit(0)
    
    # Sort news by date (newest first)
    all_news.sort(key=lambda x: x.get('datetime', 0), reverse=True)
    
    print(f"✅ TOTAL NEWS ARTICLES FOUND: {len(all_news)}")
    print_separator()
    
    # Prepare output
    output_lines = []
    output_lines.append("="*80)
    output_lines.append(f"STOCK NEWS REPORT FOR: {stock_name.upper()}")
    output_lines.append(f"DATE RANGE: {from_date_str} to {to_date_str}")
    output_lines.append(f"TOTAL ARTICLES: {len(all_news)}")
    output_lines.append(f"GENERATED ON: {datetime.now().strftime('%d %B %Y, %I:%M %p IST')}")
    output_lines.append("="*80)
    
    # Format each article
    for idx, article in enumerate(all_news, 1):
        formatted = format_news_article(article, idx)
        output_lines.append(formatted)
        
        # Print to console
        print(formatted)
        
        # Add small delay to make it readable
        if idx < len(all_news):
            time.sleep(0.1)
    
    # Save to file
    output_text = '\n'.join(output_lines)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{stock_name.upper()}_news_{from_date_str}_to_{to_date_str}_{timestamp}.txt"
    
    print_separator()
    print(f"💾 Saving results to file: {filename}")
    
    if save_to_file(output_text, filename):
        print(f"✅ Successfully saved to {filename}")
    else:
        print("❌ Failed to save file")
    
    print_separator()
    print("🎉 NEWS FETCHING COMPLETED!")
    print(f"📊 Total articles retrieved: {len(all_news)}")
    print(f"📁 Output file: {filename}")
    print_separator()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ An unexpected error occurred: {e}")
        sys.exit(1)