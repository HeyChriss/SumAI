from firecrawl import FirecrawlApp
import os

def scrape_and_crawl_website(url):
    """
    Function to scrape and crawl a website using Firecrawl.
    
    Parameters:
    url (str): The URL of the website to scrape and crawl
    crawl_limit (int): Limit for the number of pages to crawl
    """
    # Load API Key from environment variable
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("Firecrawl API key not found. Please set FIRECRAWL_API_KEY in your environment variables.")

    # Initialize Firecrawl app
    app = FirecrawlApp(api_key=api_key)

    # Scrape the website
    print(f"Scraping {url}...")
    scrape_result = app.scrape_url(
        url,
        params={'formats': ['markdown', 'html']}
    )

    # Print extracted data
    if isinstance(scrape_result, dict) and "data" in scrape_result:
        return scrape_result["data"]
    else:
        return scrape_result  # Fallback if data attribute doesn't exist


