import requests
import json
from datetime import datetime, timedelta
import time
import os

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print program header"""
    print("=" * 70)
    print(" " * 15 + "INDIAN STOCK NEWS FETCHER")
    print(" " * 20 + "(NSE & BSE Markets)")
    print("=" * 70)
    print()

def get_stock_input():
    """Get stock symbol from user"""
    while True:
        print("Enter stock symbol (e.g., RELIANCE, TCS, INFY):")
        stock = input("> ").strip().upper()
        if stock:
            return stock
        print("Please enter a valid stock symbol!\n")

def get_days_input():
    """Get number of days from user"""
    while True:
        print("\nEnter number of days (1-365):")
        try:
            days = int(input("> ").strip())
            if 1 <= days <= 365:
                return days
            print("Please enter a number between 1 and 365!\n")
        except ValueError:
            print("Please enter a valid number!\n")

def fetch_marketaux_news(stock, days, api_key):
    """Fetch news from Marketaux API"""
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for API
    published_after = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Marketaux API endpoint
    base_url = "https://api.marketaux.com/v1/news/all"
    
    # Parameters for Indian stocks
    params = {
        "api_token": api_key,
        "symbols": stock,
        "filter_entities": "true",
        "language": "en",
        "published_after": published_after,
        "sort": "published_on",
        "limit": 100,  # Maximum per request
        "must_have_entities": "true"  # Ensures better content quality
    }
    
    print(f"\nFetching news for {stock} from last {days} days...")
    print("Please wait...\n")
    
    all_articles = []
    page = 1
    
    try:
        while True:
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])
                
                if not articles:
                    break
                
                all_articles.extend(articles)
                print(f"Fetched page {page} - {len(articles)} articles")
                
                # Check if there's a next page
                meta = data.get('meta', {})
                if not meta.get('next'):
                    break
                
                # Get next page token
                params['page'] = page + 1
                page += 1
                
                # Rate limiting - be respectful to API
                time.sleep(1)
                
            elif response.status_code == 401:
                print("\nERROR: Invalid API key!")
                print("Please get your free API key from: https://www.marketaux.com/")
                return None
            elif response.status_code == 429:
                print("\nERROR: Rate limit exceeded. Please try again later.")
                return None
            else:
                print(f"\nERROR: Failed to fetch news (Status: {response.status_code})")
                return None
                
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Network error - {str(e)}")
        return None
    
    return all_articles

def format_article(article, index):
    """Format a single article for display"""
    
    separator = "=" * 70
    
    output = f"\n{separator}\n"
    output += f"ARTICLE #{index}\n"
    output += f"{separator}\n\n"
    
    # Title
    output += f"TITLE:\n{article.get('title', 'No title')}\n\n"
    
    # Published date
    published = article.get('published_at', 'Unknown date')
    try:
        dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
        output += f"PUBLISHED: {formatted_date}\n\n"
    except:
        output += f"PUBLISHED: {published}\n\n"
    
    # Source
    source = article.get('source', 'Unknown source')
    output += f"SOURCE: {source}\n\n"
    
    # URL
    url = article.get('url', 'No URL')
    output += f"URL: {url}\n\n"
    
    # Entities (related stocks/topics)
    entities = article.get('entities', [])
    if entities:
        entity_names = [e.get('name', '') for e in entities if e.get('name')]
        if entity_names:
            output += f"RELATED: {', '.join(entity_names)}\n\n"
    
    # Get all possible content fields and combine them
    description = article.get('description', '')
    snippet = article.get('snippet', '')
    
    # Try to get the longest/most complete content
    all_content = []
    
    if description:
        all_content.append(("DESCRIPTION", description))
    
    if snippet and snippet != description:
        all_content.append(("FULL CONTENT", snippet))
    
    # If there's any content, display it
    if all_content:
        output += "=" * 70 + "\n"
        output += "NEWS CONTENT:\n"
        output += "=" * 70 + "\n\n"
        for label, content in all_content:
            output += f"{content}\n\n"
    else:
        output += "CONTENT: No detailed content available for this article.\n\n"
    
    output += f"READ FULL ARTICLE AT: {url}\n\n"
    
    return output

def save_to_file(stock, days, articles):
    """Save articles to text file"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{stock}_news_{days}days_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 70 + "\n")
            f.write(f"STOCK NEWS REPORT FOR: {stock}\n")
            f.write(f"PERIOD: Last {days} days\n")
            f.write(f"GENERATED: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
            f.write(f"TOTAL ARTICLES: {len(articles)}\n")
            f.write("=" * 70 + "\n")
            
            # Write all articles
            for idx, article in enumerate(articles, 1):
                f.write(format_article(article, idx))
            
            # Write footer
            f.write("\n" + "=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")
        
        return filename
    except Exception as e:
        print(f"\nERROR: Could not save file - {str(e)}")
        return None

def display_articles(articles):
    """Display articles on screen"""
    
    print("\n" + "=" * 70)
    print(f"FOUND {len(articles)} ARTICLES")
    print("=" * 70)
    
    for idx, article in enumerate(articles, 1):
        print(format_article(article, idx))
        
        # Pause after every 5 articles for better readability
        if idx % 5 == 0 and idx < len(articles):
            input("\nPress Enter to continue...")

def main():
    """Main program function"""
    
    clear_screen()
    print_header()
    
    # API Key input
    print("Enter your Marketaux API key:")
    print("(Get free key from: https://www.marketaux.com/)")
    api_key = input("> ").strip()
    
    if not api_key:
        print("\nERROR: API key is required!")
        return
    
    print("\n")
    
    # Get user inputs
    stock = get_stock_input()
    days = get_days_input()
    
    # Fetch news
    articles = fetch_marketaux_news(stock, days, api_key)
    
    if articles is None:
        print("\nFailed to fetch news. Please try again.")
        return
    
    if len(articles) == 0:
        print(f"\nNo news found for {stock} in the last {days} days.")
        print("Try a different stock symbol or increase the number of days.")
        return
    
    # Display articles
    display_articles(articles)
    
    # Save to file
    print("\n" + "=" * 70)
    print("Saving to file...")
    filename = save_to_file(stock, days, articles)
    
    if filename:
        print(f"\nSUCCESS! News saved to: {filename}")
    
    print("\n" + "=" * 70)
    print("Thank you for using Indian Stock News Fetcher!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()