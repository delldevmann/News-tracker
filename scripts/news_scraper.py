#!/usr/bin/env python3
"""
Google News Scraper - Fetches news articles for specified keywords
and updates the README.md file with the results.
"""

import os
import re
import json
import datetime
import feedparser
import hashlib
from urllib.parse import quote
import pytz

# Constants
README_PATH = "README.md"
CACHE_PATH = ".github/scripts/news_cache.json"
MAX_ARTICLES_PER_KEYWORD = 5
TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

def get_keywords():
    """Get keywords from environment variables or use defaults."""
    keywords_str = os.environ.get("KEYWORDS", "ai, machine learning, data science")
    return [keyword.strip() for keyword in keywords_str.split(",")]

def fetch_google_news(keyword):
    """Fetch news from Google News RSS feed for a given keyword."""
    encoded_keyword = quote(keyword)
    feed_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    
    articles = []
    for entry in feed.entries[:MAX_ARTICLES_PER_KEYWORD]:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'source': entry.source.title if hasattr(entry, 'source') else "Unknown source",
            'keyword': keyword,
            'id': hashlib.md5(entry.link.encode()).hexdigest()  # Create unique ID based on URL
        }
        articles.append(article)
    
    return articles

def load_cache():
    """Load the previous news cache if it exists."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'last_updated': '', 'articles': []}

def save_cache(cache):
    """Save the news cache to a file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def update_readme(articles, last_updated):
    """Update the README.md file with the latest news articles."""
    # Create README if it doesn't exist
    if not os.path.exists(README_PATH):
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write("# News Tracker\n\n")
    
    # Read the current README content
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the news section or create it
    news_section_pattern = r"## Latest News.*?(?=^#|\Z)"
    news_section = re.search(news_section_pattern, content, re.DOTALL | re.MULTILINE)
    
    # Prepare the new news section
    new_news_section = f"## Latest News\n\n_Last updated: {last_updated}_\n\n"
    
    # Group articles by keyword
    keywords = get_keywords()
    for keyword in keywords:
        keyword_articles = [a for a in articles if a['keyword'] == keyword]
        if keyword_articles:
            new_news_section += f"### {keyword.title()}\n\n"
            for article in keyword_articles:
                new_news_section += f"- [{article['title']}]({article['link']}) - {article['source']}\n"
            new_news_section += "\n"
    
    # Replace or append the news section
    if news_section:
        content = content.replace(news_section.group(0), new_news_section)
    else:
        content += "\n\n" + new_news_section
    
    # Write the updated content back to README
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Load existing cache
    cache = load_cache()
    existing_ids = {article['id'] for article in cache['articles']}
    
    # Fetch new articles for each keyword
    all_articles = []
    keywords = get_keywords()
    for keyword in keywords:
        print(f"Fetching news for keyword: {keyword}")
        articles = fetch_google_news(keyword)
        all_articles.extend(articles)
    
    # Remove duplicates by keeping only new articles
    new_articles = [article for article in all_articles if article['id'] not in existing_ids]
    
    # Combine with existing articles and limit to most recent ones
    combined_articles = new_articles + cache['articles']
    
    # Sort by publication date (if available) or keep original order
    try:
        combined_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
    except Exception:
        # If sorting fails, just keep the original order
        pass
    
    # Keep only a reasonable number of articles per keyword
    articles_by_keyword = {}
    for article in combined_articles:
        keyword = article['keyword']
        if keyword not in articles_by_keyword:
            articles_by_keyword[keyword] = []
        
        if len(articles_by_keyword[keyword]) < MAX_ARTICLES_PER_KEYWORD:
            articles_by_keyword[keyword].append(article)
    
    # Flatten the dictionary back to a list
    filtered_articles = []
    for keyword_articles in articles_by_keyword.values():
        filtered_articles.extend(keyword_articles)
    
    # Update the timestamp
    now = datetime.datetime.now(pytz.timezone('UTC'))
    last_updated = now.strftime(TIME_FORMAT)
    
    # Update README
    if new_articles:  # Only update if there are new articles
        print(f"Found {len(new_articles)} new articles. Updating README...")
        update_readme(filtered_articles, last_updated)
    else:
        print("No new articles found.")
    
    # Update and save cache
    cache['last_updated'] = last_updated
    cache['articles'] = filtered_articles
    save_cache(cache)

if __name__ == "__main__":
    main()
