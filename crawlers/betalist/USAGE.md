# Betalist Crawler Usage Guide

## Overview
This crawler extracts startup data from betalist.com and saves it to JSON/CSV files.

## Quick Start

### Basic Usage
```bash
cd /home/user/general-data-collector/crawlers/betalist
python3 crawler.py
```

This will:
- Crawl 5 pages of startups from betalist.com
- Save results to `data/betalist/betalist_TIMESTAMP.json`
- Save results to `data/betalist/betalist_TIMESTAMP.csv`

### Output Format
Each startup entry includes:
- `source`: Always "betalist"
- `url`: The page URL that was scraped
- `scraped_at`: ISO timestamp of when data was collected
- `title`: Startup name
- `description`: Startup description
- `link`: Link to startup details
- `category`: Startup category (if available)
- `date`: Launch/post date (if available)
- `logo`: Logo URL (if available)

### Example Output
```json
[
  {
    "source": "betalist",
    "url": "https://betalist.com/",
    "scraped_at": "2025-11-17T19:18:40.845700",
    "title": "Example Startup",
    "description": "A revolutionary AI-powered tool",
    "link": "https://betalist.com/startups/example",
    "category": "Developer Tools",
    "date": "2025-11-15",
    "logo": "https://betalist.com/logos/example.png"
  }
]
```

## Customization

### Python Script Usage
```python
import asyncio
from crawler import BetalistCrawler

async def main():
    async with BetalistCrawler(
        output_dir="my_data",  # Custom output directory
        rate_limit=2.0,        # Wait 2 seconds between requests
        max_retries=3,         # Retry failed requests 3 times
        timeout=30             # 30 second timeout
    ) as crawler:
        # Crawl 10 pages
        await crawler.crawl(max_pages=10)

        # Save to custom filename
        crawler.save_json("my_startups.json")
        crawler.save_csv("my_startups.csv")

asyncio.run(main())
```

## Troubleshooting

### Network Issues
If you see "Cannot connect" errors:
- Check your internet connection
- Verify betalist.com is accessible
- Try increasing the timeout: `BetalistCrawler(timeout=60)`

### No Data Collected
If the crawler runs but collects no data:
- The website structure may have changed
- Check the logs for parsing errors
- Adjust the CSS selectors in `parse_page()` method

### Rate Limiting
If you get HTTP 429 errors:
- Increase rate_limit: `BetalistCrawler(rate_limit=3.0)`
- Reduce max_pages to crawl fewer pages

## Demo Mode
To see example output without network access:
```bash
python3 demo.py
```

This creates a sample JSON file showing the expected data structure.
