# Officer Profile Crawler Usage Guide

## Overview
Extract detailed information from Companies House officer profile pages.

## Purpose
This crawler is designed to:
- Take officer profile URLs as input
- Extract detailed officer information
- Get all appointments (current and resigned)
- Collect company associations

## Quick Start

### 1. Prepare Input File

Create `officer_urls.txt` with officer profile URLs (one per line):

```
https://find-and-update.company-information.service.gov.uk/officers/abc123xyz/appointments
https://find-and-update.company-information.service.gov.uk/officers/def456uvw/appointments
```

**How to get officer URLs:**
- Run `crawler_companies.py` first to get companies with officers
- Extract `officer_link` values from the JSON output
- Put them in `officer_urls.txt`

### 2. Run the Crawler

```bash
python3 crawler_profiles.py
```

### 3. Output
Results saved to `data/companies_house/officers_TIMESTAMP.json`

## Output Format

Each officer profile includes:

### Officer Information
- `officer_id`: Unique officer ID from Companies House
- `officer_name`: Full name
- `profile_url`: Link to profile page
- `date_of_birth`: Date of birth (if public)
- `nationality`: Nationality
- `appointment_count`: Total number of appointments
- `active_appointments`: Number of active appointments
- `resigned_appointments`: Number of resigned appointments

### Appointments List
Each appointment in the `appointments` array includes:
- `company_name`: Name of the company
- `company_link`: Link to company profile
- `company_number`: UK company registration number
- `role`: Position (Director, Secretary, etc.)
- `status`: Active or Resigned
- `appointed_on`: Appointment date
- `resigned_on`: Resignation date (if applicable)

### Example Output

```json
[
  {
    "source": "companies_house_uk",
    "scraped_at": "2025-11-20T12:00:00.000000",
    "profile_url": "https://find-and-update.company-information.service.gov.uk/officers/abc123xyz/appointments",
    "officer_id": "abc123xyz",
    "officer_name": "JOHN DOE",
    "nationality": "British",
    "appointment_count": 5,
    "active_appointments": 3,
    "resigned_appointments": 2,
    "appointments": [
      {
        "company_name": "EXAMPLE LTD",
        "company_link": "https://find-and-update.company-information.service.gov.uk/company/12345678",
        "company_number": "12345678",
        "role": "Director",
        "status": "Active",
        "appointed_on": "1 March 2020"
      },
      {
        "company_name": "ANOTHER COMPANY LTD",
        "company_link": "https://find-and-update.company-information.service.gov.uk/company/87654321",
        "company_number": "87654321",
        "role": "Director",
        "status": "Resigned",
        "appointed_on": "15 June 2018",
        "resigned_on": "30 December 2022"
      }
    ]
  }
]
```

## Typical Workflow

### Step 1: Get Companies
```bash
python3 crawler_companies.py
```
This creates `companies_TIMESTAMP.json` with company data and officer links.

### Step 2: Extract Officer URLs
From the output JSON, extract all `officer_link` values:
```python
import json

with open('data/companies_house/companies_20251120_120000.json') as f:
    companies = json.load(f)

officer_urls = []
for company in companies:
    for officer in company.get('officers', []):
        if 'officer_link' in officer:
            officer_urls.append(officer['officer_link'])

# Save to file
with open('officer_urls.txt', 'w') as f:
    for url in officer_urls:
        f.write(url + '\n')
```

### Step 3: Get Detailed Officer Profiles
```bash
python3 crawler_profiles.py
```
This creates `officers_TIMESTAMP.json` with detailed officer information.

## Python API Usage

```python
import asyncio
from crawler_profiles import OfficerProfileCrawler

async def main():
    profile_urls = [
        "https://find-and-update.company-information.service.gov.uk/officers/abc123xyz/appointments",
        "https://find-and-update.company-information.service.gov.uk/officers/def456uvw/appointments",
    ]

    async with OfficerProfileCrawler(
        output_dir="my_data",
        rate_limit=2.0,
        debug_html=True
    ) as crawler:
        await crawler.crawl(profile_urls)
        crawler.save_json("officer_profiles.json")

asyncio.run(main())
```

## Features

- **Detailed Profiles**: Extracts all available officer information
- **All Appointments**: Gets both current and resigned positions
- **Company Links**: Includes links back to company profiles
- **Rate Limiting**: Built-in 2-second delay between requests
- **Debug Mode**: Save HTML files for inspection

## Use Cases

1. **Director Network Analysis**: Map connections between directors and companies
2. **Due Diligence**: Check officer's full appointment history
3. **Risk Assessment**: Identify officers with multiple resignations
4. **Corporate Research**: Track career progression of key individuals

## Troubleshooting

### Invalid URLs
If you get errors, ensure URLs follow this format:
```
https://find-and-update.company-information.service.gov.uk/officers/{OFFICER_ID}/appointments
```

### No Appointments Found
- The officer page might not be publicly accessible
- The HTML structure may have changed
- Enable `debug_html=True` to save pages for inspection

### Rate Limiting
If you get HTTP 429 errors:
- Increase rate_limit: `OfficerProfileCrawler(rate_limit=3.0)`
- Process URLs in smaller batches

## Notes

- This crawler is designed for bulk officer profile extraction
- Each profile fetch makes 1 request
- Respects rate limits with configurable delays
- Officer URLs can be obtained from company search results
