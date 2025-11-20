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

The crawler now fetches **detailed company information** from each company's profile page (Overview tab) **plus officer information**.

### Company Fields
Each company entry includes:
- `source`: Always "companies_house_uk"
- `search_query`: The search term used
- `scraped_at`: ISO timestamp
- `company_link`: Link to full company profile
- `company_number`: UK company registration number
- `company_name`: Official company name
- `company_status`: Active, Dissolved, etc.
- `company_type`: Public limited company, Private limited, etc.
- `incorporation_date`: Date company was incorporated
- `registered_address`: Company registered address
- `nature_of_business`: SIC codes and business description
- `accounts_info`: Next accounts filing information
- `confirmation_statement`: Next confirmation statement due date
- `officers`: **NEW** - List of company officers (directors, secretaries, etc.)
- `officer_count`: **NEW** - Total number of officers
- Plus any other fields found on the Overview tab

### Officer Fields
Each officer in the `officers` list includes:
- `officer_name`: Full name of the officer
- `officer_link`: Link to officer's profile page
- `role`: Position (Director, Secretary, etc.)
- `appointed_on`: Appointment date
- `resigned_on`: Resignation date (if applicable)
- `nationality`: Officer's nationality
- `occupation`: Stated occupation
- `country_of_residence`: Country of residence
- `address`: Service/correspondence address
- Plus any other fields found on the officer page

### Example Output
```json
[
  {
    "source": "companies_house_uk",
    "search_query": "HSBC Holdings",
    "scraped_at": "2025-11-18T11:00:00.000000",
    "company_link": "https://find-and-update.company-information.service.gov.uk/company/00617987",
    "company_number": "00617987",
    "company_name": "HSBC HOLDINGS PLC",
    "company_status": "Active",
    "company_type": "Public limited company",
    "incorporation_date": "27 July 1990",
    "registered_address": "8 Canada Square, London, E14 5HQ",
    "nature_of_business": "64191 - Banks",
    "accounts_info": "Next accounts made up to 31 December 2025 due by 30 September 2026",
    "confirmation_statement": "Next statement date 31 December 2025 due by 14 January 2026",
    "officers": [
      {
        "officer_name": "JOHN DOE",
        "officer_link": "https://find-and-update.company-information.service.gov.uk/officers/abc123xyz/appointments",
        "role": "Director",
        "appointed_on": "1 March 2020",
        "nationality": "British",
        "occupation": "Company Director",
        "country_of_residence": "United Kingdom",
        "address": "8 Canada Square, London, E14 5HQ"
      },
      {
        "officer_name": "JANE SMITH",
        "officer_link": "https://find-and-update.company-information.service.gov.uk/officers/def456uvw/appointments",
        "role": "Secretary",
        "appointed_on": "15 June 2018",
        "nationality": "British",
        "occupation": "Company Secretary",
        "country_of_residence": "United Kingdom",
        "address": "8 Canada Square, London, E14 5HQ"
      }
    ],
    "officer_count": 2
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
- The crawler now automatically visits company profile pages for detailed information
- **Officer data is fetched automatically** from the `/officers` endpoint for each company
- The crawler respects rate limits with a 2-second delay between requests
- Each company lookup makes 2 requests: one for company profile, one for officers
