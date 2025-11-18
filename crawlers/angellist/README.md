# www.angellist.com Web Crawler

A production-ready, asynchronous web crawler for extracting data from [www.angellist.com](https://www.angellist.com/).

## Description

Platform for startups, angel investors, and job seekers

## Features

- **Asynchronous I/O**: Built with `aiohttp` for high-performance concurrent requests
- **Rate Limiting**: Respects server resources with configurable delays
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
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
from crawler import AngellistCrawler

async def main():
    async with AngellistCrawler(output_dir="data") as crawler:
        data = await crawler.crawl()
        crawler.save_json("results.json")
        print(f"Collected {len(data)} items")

asyncio.run(main())
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
angellist/
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
