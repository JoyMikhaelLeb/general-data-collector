# www.gov.uk/government/organisations/companies-house Web Crawler

A production-ready, asynchronous web crawler for extracting data from [www.gov.uk/government/organisations/companies-house](https://www.gov.uk/government/organisations/companies-house).

## Description

UK companies registry crawler that extracts detailed company information including officers data.

## Features

- **Asynchronous I/O**: Built with `aiohttp` for high-performance concurrent requests
- **Rate Limiting**: Respects server resources with configurable delays
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **Officers Extraction**: Automatically fetches officers from `/officers` endpoint
- **Comprehensive Data**: Extracts company details, officers names, roles, appointment dates, and links
- **Data Export**: Save results in JSON or CSV format
- **Docker Support**: Fully containerized with Docker
- **Comprehensive Testing**: Unit tests with pytest and async support
- **Production Ready**: Logging, error handling, and monitoring

## Requirements

- Python 3.11+
- uv (Python package manager)
- Docker (optional, for containerized deployment)

## Installation

### Using uv (Recommended)

```bash
# Install dependencies
make install
```

### Using pip

```bash
pip install -e .
pip install -e ".[dev]"
```

## Usage

### Input Format

Create a `companies.txt` file with one company name per line:

```
HSBC Holdings
BP plc
Tesco
Barclays
Vodafone
```

### Command Line

```bash
# Run the crawler
make run

# Or directly with Python
python crawler.py
```

### Programmatic Usage

```python
import asyncio
from crawler import CompaniesHouseCrawler

async def main():
    companies = ["HSBC Holdings", "BP plc", "Tesco"]

    async with CompaniesHouseCrawler(output_dir="data") as crawler:
        data = await crawler.crawl(companies)
        crawler.save_json("results.json")
        print(f"Collected {len(data)} companies")

asyncio.run(main())
```

### Output Format

The crawler returns JSON with company details and officers:

```json
{
  "source": "companies_house_uk",
  "search_query": "HSBC Holdings",
  "scraped_at": "2024-11-18T12:00:00.000000",
  "company_link": "https://find-and-update.company-information.service.gov.uk/company/12345678",
  "company_number": "12345678",
  "company_name": "HSBC HOLDINGS PLC",
  "company_status": "Active",
  "company_type": "Public limited company",
  "incorporation_date": "01 January 1990",
  "registered_address": "8 Canada Square, London, E14 5HQ",
  "officers": [
    {
      "officer_name": "John Smith",
      "officer_link": "https://find-and-update.company-information.service.gov.uk/officers/ABC123XYZ/appointments",
      "role": "Director",
      "appointed_on": "15 March 2020",
      "nationality": "British",
      "occupation": "Company Director"
    }
  ],
  "officers_count": 5
}
```

## Development

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Run all validation
make validate
```

### Docker

```bash
# Build Docker image
make docker-build

# Run crawler in container
make docker-run

# Run tests in container
make docker-test
```

## Project Structure

```
companies_house/
├── crawler.py           # Main crawler implementation
├── pyproject.toml       # Project dependencies
├── Makefile            # Development commands
├── Dockerfile          # Container definition
├── README.md           # This file
├── ARCHITECTURE.md     # Architecture documentation
├── tests/
│   └── test_crawler.py # Test suite
└── data/               # Output directory
```

## License

MIT License

## Support

For issues and questions, check the ARCHITECTURE.md for technical details.
