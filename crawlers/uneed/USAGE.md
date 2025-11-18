# Uneed.best Crawler Usage Guide

## Overview
This crawler extracts daily tool launches from uneed.best and fetches detailed information for each tool.

## Quick Start

### Run the Crawler
```bash
cd /home/user/general-data-collector/crawlers/uneed
python3 crawler.py
```

This will:
- Crawl the main page at https://www.uneed.best
- Find all tool links (containing /tool/)
- Visit each tool page to extract detailed information
- Save results to `data/uneed/uneed_TIMESTAMP.json`

## Output Format

Each tool entry includes:
- `source`: Always "uneed_best"
- `scraped_at`: ISO timestamp
- `tool_url`: Link to tool page on uneed.best
- `tool_name`: Name of the tool
- `overview`: Tool description/overview
- `website`: Tool's official website
- `publisher_name`: Name of the person/company who published
- `publisher_link`: Link to publisher profile
- `launch_date`: When the tool was launched
- `category`: Tool category
- `pricing`: Pricing information
- `socials`: Social media links (Twitter, LinkedIn, etc.)
- `for_sale`: Whether the tool is for sale

### Example Output
```json
[
  {
    "source": "uneed_best",
    "scraped_at": "2025-11-18T12:00:00.000000",
    "tool_url": "https://www.uneed.best/tool/ai-design-assistant",
    "tool_name": "AI Design Assistant",
    "overview": "Revolutionary AI-powered design tool that helps you create stunning visuals in minutes",
    "website": "https://example-tool.com",
    "publisher_name": "John Smith",
    "publisher_link": "https://www.uneed.best/user/johnsmith",
    "launch_date": "2025-11-18",
    "category": "Design Tools",
    "pricing": "Free with premium options",
    "socials": {
      "twitter": "https://twitter.com/exampletool",
      "linkedin": "https://linkedin.com/company/exampletool"
    },
    "for_sale": false
  }
]
```

## Python API Usage

```python
import asyncio
from crawler import UneedCrawler

async def main():
    async with UneedCrawler(
        output_dir="my_data",
        rate_limit=2.0,  # 2 seconds between requests
        timeout=30
    ) as crawler:
        # Crawl from specific URL
        await crawler.crawl("https://www.uneed.best")

        # Save to custom filename
        crawler.save_json("my_tools.json")

        # Access the data
        print(f"Collected {len(crawler.data)} tools")

asyncio.run(main())
```

## Features

- **Automatic Tool Discovery**: Finds all /tool/ links on the main page
- **Detailed Extraction**: Visits each tool page for complete information
- **Rate Limiting**: Built-in 2-second delay between requests
- **Retry Logic**: Automatically retries failed requests
- **JSON Output**: Clean, structured data output
- **Social Media Links**: Extracts Twitter, LinkedIn, GitHub, etc.

## Troubleshooting

### Network Issues
If you see connection errors:
- Check your internet connection
- Try increasing the timeout: `UneedCrawler(timeout=60)`

### No Data Collected
If the crawler returns no results:
- The website structure may have changed
- Check the logs for parsing errors
- The selectors may need adjustment

### Rate Limiting
If you get HTTP 429 errors:
- Increase rate_limit: `UneedCrawler(rate_limit=3.0)`

## Demo Mode

To see example output without network access:
```bash
python3 demo.py
```

This creates a sample JSON file showing the expected data structure.
