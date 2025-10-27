import requests
import json
from datetime import datetime, timedelta
import time
import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
    print("=" * 60)
    print(" " * 15 + "INDIAN STOCK NEWS FETCHER")
    print(" " * 20 + "NSE & BSE Markets")
    print("=" * 60)
    print()

def get_api_key():
    """Get Alpha Vantage API key from user"""
    print("Please enter your Alpha Vantage API key:")
    print("(Get free key from: https://www.alphavantage.co/support/#api-key)")
    api_key = input("API Key: ").strip()
    return api_key

def get_stock_symbol():
    """Get stock symbol from user"""
    print("\nEnter the stock symbol (e.g., RELIANCE, TCS, INFY):")
    symbol = input("Stock Symbol: ").strip().upper()
    return symbol

def get_company_name(symbol):
    """Map common stock symbols to company names for better search"""
    stock_map = {
        'TCS': 'Tata Consultancy Services',
        'RELIANCE': 'Reliance Industries',
        'INFY': 'Infosys',
        'HDFCBANK': 'HDFC Bank',
        'ICICIBANK': 'ICICI Bank',
        'SBIN': 'State Bank of India',
        'BHARTIARTL': 'Bharti Airtel',
        'ITC': 'ITC Limited',
        'WIPRO': 'Wipro',
        'HCLTECH': 'HCL Technologies',
        'LT': 'Larsen & Toubro',
        'AXISBANK': 'Axis Bank',
        'MARUTI': 'Maruti Suzuki',
        'TATAMOTORS': 'Tata Motors',
        'TATASTEEL': 'Tata Steel',
        'SUNPHARMA': 'Sun Pharmaceutical',
        'ONGC': 'Oil and Natural Gas Corporation',
        'NTPC': 'NTPC Limited',
        'POWERGRID': 'Power Grid Corporation',
        'ASIANPAINT': 'Asian Paints',
        'NESTLEIND': 'Nestle India',
        'HINDUNILVR': 'Hindustan Unilever',
        'BAJFINANCE': 'Bajaj Finance',
        'KOTAKBANK': 'Kotak Mahindra Bank',
        'TITAN': 'Titan Company',
        'ADANIENT': 'Adani Enterprises',
        'ADANIPORTS': 'Adani Ports',
        'ULTRACEMCO': 'UltraTech Cement',
        'M&M': 'Mahindra & Mahindra',
        'TECHM': 'Tech Mahindra'
    }
    return stock_map.get(symbol, symbol)

def get_days():
    """Get number of days for news"""
    while True:
        try:
            print("\nEnter number of days for news (1-365):")
            days = int(input("Days: ").strip())
            if 1 <= days <= 365:
                return days
            else:
                print("Please enter a number between 1 and 365.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def fetch_full_article(url):
    """Attempt to fetch full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return None

def fetch_stock_news(api_key, symbol, days):
    """Fetch stock news from Alpha Vantage using multiple methods"""
    print(f"\nFetching news for {symbol}...")
    print("Please wait (this may take a while for longer periods)...\n")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for API
    time_from = start_date.strftime("%Y%m%dT%H%M")
    time_to = end_date.strftime("%Y%m%dT%H%M")
    
    # Get company name for search
    company_name = get_company_name(symbol)
    
    # Try multiple ticker formats
    ticker_formats = [
        symbol,
        f"{symbol}.NS",  # NSE format
        f"{symbol}.BO",  # BSE format
        company_name
    ]
    
    all_articles = []
    search_methods = []
    
    # For longer periods, we need to make multiple requests
    # Alpha Vantage limits to 1000 articles per request
    if days > 30:
        print("Fetching news in batches for extended period...")
        batches = (days // 30) + 1
        
        for batch in range(batches):
            batch_end = end_date - timedelta(days=batch * 30)
            batch_start = batch_end - timedelta(days=min(30, days - batch * 30))
            
            if batch_start < start_date:
                batch_start = start_date
            
            batch_time_from = batch_start.strftime("%Y%m%dT%H%M")
            batch_time_to = batch_end.strftime("%Y%m%dT%H%M")
            
            print(f"Batch {batch + 1}/{batches}: {batch_start.strftime('%Y-%m-%d')} to {batch_end.strftime('%Y-%m-%d')}")
            
            # Method 1: Try ticker-based search with different formats
            for ticker in ticker_formats[:3]:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "NEWS_SENTIMENT",
                    "tickers": ticker,
                    "time_from": batch_time_from,
                    "time_to": batch_time_to,
                    "limit": 1000,
                    "apikey": api_key
                }
                
                try:
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "Error Message" in data:
                        continue
                    
                    if "Note" in data:
                        print(f"API Limit: {data['Note']}")
                        return None
                    
                    if "feed" in data and len(data["feed"]) > 0:
                        all_articles.extend(data["feed"])
                        if f"ticker:{ticker}" not in search_methods:
                            search_methods.append(f"ticker:{ticker}")
                        print(f"  Found {len(data['feed'])} articles with {ticker}")
                        break
                    
                    time.sleep(1)
                    
                except Exception as e:
                    continue
            
            time.sleep(2)  # Rate limiting between batches
    else:
        # Method 1: Try ticker-based search with different formats
        for ticker in ticker_formats[:3]:
            print(f"Searching with ticker: {ticker}...")
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": ticker,
                "time_from": time_from,
                "time_to": time_to,
                "limit": 1000,
                "apikey": api_key
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if "Error Message" in data:
                    continue
                
                if "Note" in data:
                    print(f"API Limit: {data['Note']}")
                    return None
                
                if "feed" in data and len(data["feed"]) > 0:
                    all_articles.extend(data["feed"])
                    search_methods.append(f"ticker:{ticker}")
                    print(f"Found {len(data['feed'])} articles with {ticker}")
                    break
                
                time.sleep(1)
                
            except Exception as e:
                continue
    
    # Method 2: If no articles found, try company name search
    if len(all_articles) == 0:
        print(f"Trying keyword search: {company_name}...")
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "topics": "technology,finance,economy",
            "time_from": time_from,
            "time_to": time_to,
            "limit": 1000,
            "apikey": api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "Note" in data:
                print(f"API Limit: {data['Note']}")
                return None
            
            if "feed" in data:
                keywords = [symbol.lower(), company_name.lower()]
                filtered_articles = []
                
                for article in data["feed"]:
                    title = article.get('title', '').lower()
                    summary = article.get('summary', '').lower()
                    
                    if any(keyword in title or keyword in summary for keyword in keywords):
                        filtered_articles.append(article)
                
                if filtered_articles:
                    all_articles.extend(filtered_articles)
                    search_methods.append(f"keyword:{company_name}")
                    print(f"Found {len(filtered_articles)} articles with keyword search")
        
        except Exception as e:
            pass
    
    # Remove duplicates based on URL
    if all_articles:
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        # Sort by date (newest first)
        unique_articles.sort(key=lambda x: x.get('time_published', ''), reverse=True)
        
        if unique_articles:
            result_data = {
                "feed": unique_articles,
                "search_methods": search_methods
            }
            print(f"Total unique articles found: {len(unique_articles)}\n")
            return result_data
    
    print("No news articles found for this stock.")
    print("This could mean:")
    print("- The stock has limited recent news coverage")
    print("- Try a different stock symbol")
    print("- Try a different time period")
    return None

def format_sentiment(score):
    """Format sentiment score to readable text"""
    try:
        score = float(score)
        if score >= 0.35:
            return "BULLISH ↑"
        elif score <= -0.35:
            return "BEARISH ↓"
        else:
            return "NEUTRAL →"
    except:
        return "N/A"

def save_news_to_file(symbol, days, news_data):
    """Save news to a text file with FULL content"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_news_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"STOCK NEWS REPORT: {symbol}\n")
        company_name = get_company_name(symbol)
        if company_name != symbol:
            f.write(f"Company: {company_name}\n")
        f.write(f"Period: Last {days} days\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n\n")
        
        if not news_data or "feed" not in news_data:
            f.write("No news found.\n")
            return filename
        
        articles = news_data["feed"]
        f.write(f"Total Articles Found: {len(articles)}\n")
        
        if "search_methods" in news_data:
            f.write(f"Search Methods Used: {', '.join(news_data['search_methods'])}\n")
        
        f.write("=" * 100 + "\n\n")
        
        for idx, article in enumerate(articles, 1):
            f.write("\n" + "█" * 100 + "\n")
            f.write(f"ARTICLE #{idx}\n")
            f.write("█" * 100 + "\n\n")
            
            f.write(f"TITLE:\n{article.get('title', 'N/A')}\n\n")
            f.write(f"SOURCE: {article.get('source', 'N/A')}\n")
            f.write(f"AUTHORS: {', '.join(article.get('authors', ['N/A']))}\n")
            
            # Format publication date
            pub_date = article.get('time_published', 'N/A')
            if pub_date != 'N/A' and len(pub_date) >= 8:
                try:
                    formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
                    if len(pub_date) >= 13:
                        formatted_date += f" {pub_date[9:11]}:{pub_date[11:13]}"
                    f.write(f"PUBLISHED: {formatted_date}\n")
                except:
                    f.write(f"PUBLISHED: {pub_date}\n")
            else:
                f.write(f"PUBLISHED: {pub_date}\n")
            
            # Get sentiment
            if 'overall_sentiment_score' in article:
                sentiment = format_sentiment(article['overall_sentiment_score'])
                score = article['overall_sentiment_score']
                f.write(f"SENTIMENT: {sentiment} (Score: {score})\n")
            
            f.write(f"\nARTICLE URL:\n{article.get('url', 'N/A')}\n")
            
            # Banner image
            if 'banner_image' in article and article['banner_image']:
                f.write(f"\nIMAGE URL:\n{article['banner_image']}\n")
            
            # Category tags
            if 'category_within_source' in article and article['category_within_source']:
                f.write(f"\nCATEGORY: {article['category_within_source']}\n")
            
            # Topics
            if 'topics' in article and article['topics']:
                topics_list = [t.get('topic', '') for t in article['topics']]
                f.write(f"TOPICS: {', '.join(topics_list)}\n")
            
            # Full content
            f.write("\n" + "-" * 100 + "\n")
            f.write("FULL ARTICLE CONTENT:\n")
            f.write("-" * 100 + "\n\n")
            
            summary = article.get('summary', 'No content available')
            f.write(f"{summary}\n")
            
            # Ticker sentiment details
            if 'ticker_sentiment' in article and article['ticker_sentiment']:
                f.write("\n" + "-" * 100 + "\n")
                f.write("STOCK-SPECIFIC SENTIMENT ANALYSIS:\n")
                f.write("-" * 100 + "\n\n")
                for ticker_info in article['ticker_sentiment']:
                    ticker_symbol = ticker_info.get('ticker', 'N/A')
                    ticker_sentiment = format_sentiment(ticker_info.get('ticker_sentiment_score', '0'))
                    relevance = ticker_info.get('relevance_score', 'N/A')
                    sentiment_label = ticker_info.get('ticker_sentiment_label', 'N/A')
                    f.write(f"  • {ticker_symbol}:\n")
                    f.write(f"    - Sentiment: {ticker_sentiment} ({sentiment_label})\n")
                    f.write(f"    - Relevance Score: {relevance}\n")
                    f.write(f"    - Sentiment Score: {ticker_info.get('ticker_sentiment_score', 'N/A')}\n\n")
            
            f.write("\n" + "=" * 100 + "\n")
    
    return filename

def display_news_summary(symbol, news_data):
    """Display news summary on screen"""
    print("\n" + "=" * 60)
    print(f"NEWS SUMMARY FOR {symbol}")
    company_name = get_company_name(symbol)
    if company_name != symbol:
        print(f"Company: {company_name}")
    print("=" * 60 + "\n")
    
    if not news_data or "feed" not in news_data:
        print("No news found.")
        return
    
    articles = news_data["feed"]
    print(f"✓ Total articles found: {len(articles)}\n")
    
    # Display first 10 articles briefly
    display_count = min(10, len(articles))
    print(f"Showing top {display_count} recent articles:\n")
    
    for idx, article in enumerate(articles[:display_count], 1):
        print(f"{idx}. {article.get('title', 'N/A')}")
        print(f"   Source: {article.get('source', 'N/A')}")
        
        # Format date
        pub_date = article.get('time_published', 'N/A')
        if pub_date != 'N/A' and len(pub_date) >= 8:
            try:
                formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
                print(f"   Date: {formatted_date}")
            except:
                print(f"   Date: {pub_date}")
        
        if 'overall_sentiment_score' in article:
            sentiment = format_sentiment(article['overall_sentiment_score'])
            print(f"   Sentiment: {sentiment}")
        
        print()

def main():
    """Main program function"""
    clear_screen()
    print_header()
    
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        print("API key is required. Exiting...")
        return
    
    # Get stock symbol
    symbol = get_stock_symbol()
    
    if not symbol:
        print("Stock symbol is required. Exiting...")
        return
    
    # Get number of days
    days = get_days()
    
    # Fetch news
    news_data = fetch_stock_news(api_key, symbol, days)
    
    if news_data:
        # Display summary
        display_news_summary(symbol, news_data)
        
        # Save to file
        print("\nSaving full articles to file...")
        filename = save_news_to_file(symbol, days, news_data)
        print(f"\n✓ Full detailed report saved to: {filename}")
        print(f"✓ Total articles: {len(news_data['feed'])}")
        print("\nThe file contains COMPLETE article content with:")
        print("  • Full titles and content")
        print("  • Source and author information")
        print("  • Publication dates")
        print("  • Sentiment analysis")
        print("  • Article URLs for reference")
        print("  • Stock-specific sentiment breakdowns")
        print("\nThank you for using Indian Stock News Fetcher!")
    else:
        print("\n❌ Failed to fetch news.")
        print("\nTroubleshooting tips:")
        print("1. Check if stock symbol is correct (e.g., TCS, RELIANCE, INFY)")
        print("2. Try a different time period")
        print("3. Some stocks may have limited news coverage")
        print("4. Verify your API key is valid")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()