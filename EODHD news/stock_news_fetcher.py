import requests
import json
from datetime import datetime, timedelta
import sys

def print_header():
    """Print program header"""
    print("=" * 60)
    print("INDIAN STOCK NEWS FETCHER - NSE/BSE")
    print("Powered by EODHD API")
    print("=" * 60)
    print()

def get_api_key():
    """Get API key from user"""
    print("Enter your EODHD API Key:")
    api_key = input("> ").strip()
    if not api_key:
        print("Error: API key cannot be empty!")
        sys.exit(1)
    return api_key

def get_stock_symbol():
    """Get stock symbol from user"""
    print("\nEnter Stock Symbol (e.g., RELIANCE for NSE or RELIANCE.BSE for BSE):")
    symbol = input("> ").strip().upper()
    if not symbol:
        print("Error: Stock symbol cannot be empty!")
        sys.exit(1)
    
    # Add exchange suffix if not provided
    if '.NSE' not in symbol and '.BSE' not in symbol:
        print(f"\nNo exchange specified. Using NSE by default.")
        symbol = f"{symbol}.NSE"
    
    return symbol

def get_days():
    """Get number of days from user"""
    print("\nEnter number of days (1-365):")
    while True:
        try:
            days = int(input("> ").strip())
            if 1 <= days <= 365:
                return days
            else:
                print("Please enter a number between 1 and 365.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def fetch_news(api_key, symbol, days):
    """Fetch news from EODHD API"""
    print(f"\nFetching news for {symbol} for the last {days} days...")
    print("Please wait...\n")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates
    from_date = start_date.strftime('%Y-%m-%d')
    to_date = end_date.strftime('%Y-%m-%d')
    
    # EODHD News API endpoint
    url = f"https://eodhd.com/api/news"
    
    params = {
        'api_token': api_key,
        's': symbol,
        'from': from_date,
        'to': to_date,
        'limit': 1000,
        'offset': 0
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        news_data = response.json()
        
        if isinstance(news_data, list) and len(news_data) > 0:
            return news_data
        else:
            print(f"No news found for {symbol} in the specified date range.")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid response from API. Please check your API key.")
        return []

def format_news(news_data, symbol):
    """Format news data for display and file output"""
    if not news_data:
        return "No news articles found."
    
    output = []
    output.append("=" * 80)
    output.append(f"STOCK NEWS FOR: {symbol}")
    output.append(f"Total Articles Found: {len(news_data)}")
    output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 80)
    output.append("\n")
    
    for idx, article in enumerate(news_data, 1):
        output.append(f"\n{'=' * 80}")
        output.append(f"ARTICLE #{idx}")
        output.append(f"{'=' * 80}")
        output.append(f"\nTITLE: {article.get('title', 'N/A')}")
        output.append(f"\nDATE: {article.get('date', 'N/A')}")
        output.append(f"\nSOURCE: {article.get('source', 'N/A')}")
        
        if article.get('link'):
            output.append(f"\nLINK: {article.get('link')}")
        
        if article.get('symbols'):
            output.append(f"\nRELATED SYMBOLS: {', '.join(article.get('symbols'))}")
        
        if article.get('tags'):
            output.append(f"\nTAGS: {', '.join(article.get('tags'))}")
        
        content = article.get('content', 'No content available')
        output.append(f"\nCONTENT:\n{content}")
        output.append(f"\n{'=' * 80}\n")
    
    return "\n".join(output)

def save_to_file(content, symbol):
    """Save news to text file"""
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{symbol.replace('.', '_')}_news_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ News saved to: {filename}")
        return filename
    except Exception as e:
        print(f"\nError saving file: {e}")
        return None

def main():
    """Main function"""
    print_header()
    
    # Get user inputs
    api_key = get_api_key()
    symbol = get_stock_symbol()
    days = get_days()
    
    # Fetch news
    news_data = fetch_news(api_key, symbol, days)
    
    if news_data:
        # Format news
        formatted_news = format_news(news_data, symbol)
        
        # Display on console
        print("\n" + formatted_news)
        
        # Save to file
        save_to_file(formatted_news, symbol)
        
        print("\n" + "=" * 60)
        print("Process completed successfully!")
        print("=" * 60)
    else:
        print("\nNo news data to display or save.")
        print("\nPossible reasons:")
        print("1. Invalid API key")
        print("2. Invalid stock symbol")
        print("3. No news available for the specified date range")
        print("4. API rate limit reached")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)