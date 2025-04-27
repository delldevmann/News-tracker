# News Tracker

This repository automatically tracks news articles from Google News on selected keywords.

## How It Works

- GitHub Action runs every 6 hours
- Scrapes Google News for specified keywords
- Removes duplicate articles
- Updates this README with the latest news

## Configuration

To change the keywords being tracked, edit the `KEYWORDS` environment variable in the `.github/workflows/google-news-scraper.yml` file.

## Latest News

_Last updated: The news section will be populated after the first workflow run_
