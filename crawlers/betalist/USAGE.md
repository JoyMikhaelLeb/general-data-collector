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
- Crawl today's startups from betalist.com (1 page)
- Save results to `data/betalist/betalist_TIMESTAMP.json`

### Output Format
Each startup entry includes:
- `source`: Always "betalist"
- `url`: The page URL that was scraped
- `scraped_at`: ISO timestamp of when data was collected
- `startup_id`: Unique ID from betalist.com
- `title`: Startup name
- `description`: Startup tagline/description
- `link`: Link to startup details page
- `logo`: Logo/image URL (if available)
- `date_launched`: Launch date in DD-MM-YYYY format (extracted from page headers)

### Example Output
```json
[
  {
    "source": "betalist",
    "url": "https://betalist.com/",
    "scraped_at": "2025-11-17T19:51:50.579082",
    "startup_id": "135459",
    "title": "ClioWright",
    "description": "Never forget a subscription payment again",
    "link": "https://betalist.com/startups/cliowright",
    "logo": "https://resize.imagekit.co/wMcJKw61N4F_Zzk2Yq68wbSxuyblxuza-KnNV9fk7hY/rs:fill:480:360/plain/s3://betalist-production/r3kim3bjds8yio4tn0suetrjv2l5",
    "date_launched": "17-11-2025"
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
