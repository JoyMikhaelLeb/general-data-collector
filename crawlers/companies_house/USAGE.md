# Companies House UK Crawler Usage Guide

## Overview
This crawler searches the UK Companies House website for company information and saves results to JSON.

## Quick Start

### 1. Create Input File
Create `companies.txt` with company names (one per line):
```
HSBC Holdings
BP plc
Tesco
Barclays
Vodafone
```

### 2. Run the Crawler
```bash
cd /home/user/general-data-collector/crawlers/companies_house
python3 crawler.py
```

### 3. Output
Results are saved to `data/companies_house/companies_TIMESTAMP.json`

## Output Format
Each company entry includes:
- `source`: Always "companies_house_uk"
- `search_query`: The search term used
- `scraped_at`: ISO timestamp
- `company_number`: UK company registration number
- `company_name`: Official company name
- `company_status`: Active, Dissolved, etc.
- `registered_address`: Company registered address
- `incorporation_date`: Date company was incorporated
- `company_link`: Link to full company profile

### Example Output
```json
[
  {
    "source": "companies_house_uk",
    "search_query": "HSBC Holdings",
    "scraped_at": "2025-11-18T07:00:00.000000",
    "company_number": "00617987",
    "company_name": "HSBC HOLDINGS PLC",
    "company_status": "Active",
    "registered_address": "8 Canada Square, London, E14 5HQ",
    "incorporation_date": "27 July 1990",
    "company_link": "https://find-and-update.company-information.service.gov.uk/company/00617987"
  }
]
```

## Python API Usage

```python
import asyncio
from crawler import CompaniesHouseCrawler

async def main():
    companies = ["HSBC Holdings", "BP plc", "Tesco"]

    async with CompaniesHouseCrawler(
        output_dir="my_data",
        rate_limit=2.0,  # 2 seconds between requests
        timeout=30
    ) as crawler:
        await crawler.crawl(companies)
        crawler.save_json("my_companies.json")

asyncio.run(main())
```

## Features

- **Batch Processing**: Search multiple companies from a file
- **Rate Limiting**: Built-in 2-second delay between requests
- **Retry Logic**: Automatically retries failed requests
- **JSON Output**: Clean, structured data output
- **Error Handling**: Continues processing even if some searches fail

## Troubleshooting

### Network Issues
If you see connection errors:
- Check your internet connection
- Try increasing the timeout: `CompaniesHouseCrawler(timeout=60)`

### No Results Found
If searches return no results:
- Check company name spelling
- Try searching with different name variations
- Some companies may have changed names or been dissolved

### Rate Limiting
If you get HTTP 429 errors:
- Increase rate_limit: `CompaniesHouseCrawler(rate_limit=3.0)`
- Reduce the number of companies per batch

## Notes

- This crawler searches publicly available data on Companies House
- Search results may return multiple matches for a single query
- The crawler extracts data from search results pages only
- For detailed company information, you may need to visit the company_link URL
