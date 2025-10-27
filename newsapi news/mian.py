import requests
import json
from datetime import datetime, timedelta
import time
import os

class StockNewsFetcher:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://newsapi.org/v2/everything"
        
    def get_api_key(self):
        """Get API key from user"""
        print("=" * 60)
        print("INDIAN STOCK NEWS FETCHER")
        print("=" * 60)
        print("\nPlease enter your NewsAPI.org API Key:")
        print("(Get free API key from: https://newsapi.org/register)")
        api_key = input("\nAPI Key: ").strip()
        
        if not api_key:
            print("\nError: API Key cannot be empty!")
            return False
        
        self.api_key = api_key
        return True
    
    def get_stock_name(self):
        """Get stock name from user"""
        print("\n" + "-" * 60)
        print("Enter the stock name (e.g., Reliance, TCS, HDFC, Infosys):")
        stock_name = input("\nStock Name: ").strip()
        
        if not stock_name:
            print("\nError: Stock name cannot be empty!")
            return None
        
        return stock_name
    
    def get_days(self):
        """Get number of days from user"""
        print("\n" + "-" * 60)
        print("Enter number of days to fetch news (1-30):")
        print("Note: Free NewsAPI plan allows up to 30 days of historical data")
        
        while True:
            try:
                days = input("\nDays: ").strip()
                days = int(days)
                
                if days < 1:
                    print("Please enter a number greater than 0")
                    continue
                elif days > 30:
                    print("Note: Free plan limit is 30 days. Setting to 30 days.")
                    days = 30
                
                return days
            except ValueError:
                print("Please enter a valid number")
    
    def fetch_news(self, stock_name, days):
        """Fetch news from NewsAPI.org"""
        print("\n" + "=" * 60)
        print(f"FETCHING NEWS FOR: {stock_name.upper()}")
        print("=" * 60)
        print("\nPlease wait, fetching news...\n")
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Format dates for API
        to_date_str = to_date.strftime('%Y-%m-%d')
        from_date_str = from_date.strftime('%Y-%m-%d')
        
        # Build query - focus on Indian stock market
        query = f"{stock_name} AND (NSE OR BSE OR India OR stock OR share OR equity)"
        
        # API parameters
        params = {
            'q': query,
            'from': from_date_str,
            'to': to_date_str,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok':
                    articles = data.get('articles', [])
                    print(f"✓ Successfully fetched {len(articles)} articles\n")
                    return articles
                else:
                    print(f"Error: {data.get('message', 'Unknown error')}")
                    return None
            
            elif response.status_code == 401:
                print("Error: Invalid API Key. Please check your API key.")
                return None
            
            elif response.status_code == 426:
                print("Error: API request limit exceeded. Please upgrade your plan or try again later.")
                return None
            
            elif response.status_code == 429:
                print("Error: Too many requests. Please wait and try again later.")
                return None
            
            else:
                print(f"Error: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out. Please check your internet connection.")
            return None
        
        except requests.exceptions.ConnectionError:
            print("Error: Connection failed. Please check your internet connection.")
            return None
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    def save_to_file(self, articles, stock_name, days):
        """Save articles to text file"""
        if not articles:
            print("No articles to save.")
            return
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{stock_name.replace(' ', '_')}_{days}days_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"STOCK NEWS REPORT: {stock_name.upper()}\n")
                f.write(f"Period: Last {days} days\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Articles: {len(articles)}\n")
                f.write("=" * 80 + "\n\n")
                
                for idx, article in enumerate(articles, 1):
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"ARTICLE {idx}\n")
                    f.write(f"{'=' * 80}\n\n")
                    
                    f.write(f"TITLE:\n{article.get('title', 'N/A')}\n\n")
                    
                    f.write(f"SOURCE:\n{article.get('source', {}).get('name', 'N/A')}\n\n")
                    
                    f.write(f"PUBLISHED:\n{article.get('publishedAt', 'N/A')}\n\n")
                    
                    f.write(f"AUTHOR:\n{article.get('author', 'N/A')}\n\n")
                    
                    f.write(f"DESCRIPTION:\n{article.get('description', 'N/A')}\n\n")
                    
                    f.write(f"FULL CONTENT:\n{article.get('content', 'N/A')}\n\n")
                    
                    f.write(f"URL:\n{article.get('url', 'N/A')}\n\n")
                    
                    f.write("-" * 80 + "\n")
            
            print(f"\n✓ News saved successfully to: {filename}\n")
            return filename
            
        except Exception as e:
            print(f"\nError saving file: {str(e)}\n")
            return None
    
    def display_articles(self, articles):
        """Display articles in console"""
        if not articles:
            print("No articles found.")
            return
        
        print("\n" + "=" * 80)
        print(f"DISPLAYING {len(articles)} ARTICLES")
        print("=" * 80 + "\n")
        
        for idx, article in enumerate(articles, 1):
            print(f"\n{'=' * 80}")
            print(f"ARTICLE {idx}")
            print(f"{'=' * 80}\n")
            
            print(f"TITLE:\n{article.get('title', 'N/A')}\n")
            
            print(f"SOURCE:\n{article.get('source', {}).get('name', 'N/A')}\n")
            
            print(f"PUBLISHED:\n{article.get('publishedAt', 'N/A')}\n")
            
            print(f"AUTHOR:\n{article.get('author', 'N/A')}\n")
            
            print(f"DESCRIPTION:\n{article.get('description', 'N/A')}\n")
            
            print(f"FULL CONTENT:\n{article.get('content', 'N/A')}\n")
            
            print(f"URL:\n{article.get('url', 'N/A')}\n")
            
            if article.get('urlToImage'):
                print(f"IMAGE URL:\n{article.get('urlToImage')}\n")
            
            print("-" * 80)
            
            # Pause after every 5 articles for readability
            if idx % 5 == 0 and idx < len(articles):
                input("\n[Press Enter to continue...]\n")
    
    def run(self):
        """Main program loop"""
        # Get API key
        if not self.get_api_key():
            return
        
        while True:
            # Get stock name
            stock_name = self.get_stock_name()
            if not stock_name:
                continue
            
            # Get days
            days = self.get_days()
            
            # Fetch news
            articles = self.fetch_news(stock_name, days)
            
            if articles:
                # Display articles
                self.display_articles(articles)
                
                # Save to file
                self.save_to_file(articles, stock_name, days)
            else:
                print("\nNo news found or error occurred.")
            
            # Ask if user wants to search again
            print("\n" + "=" * 60)
            choice = input("Do you want to search for another stock? (yes/no): ").strip().lower()
            
            if choice not in ['yes', 'y']:
                print("\n" + "=" * 60)
                print("Thank you for using Indian Stock News Fetcher!")
                print("=" * 60 + "\n")
                break

if __name__ == "__main__":
    try:
        fetcher = StockNewsFetcher()
        fetcher.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        print("Please report this error if it persists.")