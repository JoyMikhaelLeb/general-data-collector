# Harmonic.ai Web Crawler

A production-ready, asynchronous web crawler for extracting data from [Harmonic.ai](https://harmonic.ai/).

## Features

- **Asynchronous I/O**: Built with `aiohttp` for high-performance concurrent requests
- **Rate Limiting**: Respects server resources with configurable delays
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **Data Export**: Save results in JSON or CSV format
- **Docker Support**: Fully containerized with Docker and docker-compose
- **Comprehensive Testing**: Unit tests with pytest and async support
- **Type Safety**: Type hints throughout the codebase
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

# Or manually with uv
uv pip install -e .
uv pip install -e ".[dev]"
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
from crawler import HarmonicCrawler

async def main():
    async with HarmonicCrawler(output_dir="data") as crawler:
        # Crawl the site
        data = await crawler.crawl()

        # Save results
        crawler.save_json("results.json")
        crawler.save_csv("results.csv")

        print(f"Collected {len(data)} items")

asyncio.run(main())
```

### Configuration

```python
crawler = HarmonicCrawler(
    output_dir="data",      # Output directory
    rate_limit=1.0,         # Seconds between requests
    max_retries=3,          # Maximum retry attempts
    timeout=30              # Request timeout in seconds
)
```

## Development

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast

# Run specific test file
pytest tests/test_crawler.py -v
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

# Open shell in container
make docker-shell
```

## Project Structure

```
harmonic_ai/
├── crawler.py           # Main crawler implementation
├── pyproject.toml       # Project dependencies and config
├── Makefile            # Development and deployment commands
├── Dockerfile          # Container definition
├── README.md           # This file
├── ARCHITECTURE.md     # Architecture documentation
├── tests/
│   └── test_crawler.py # Test suite
└── data/               # Output directory (created at runtime)
```

## Output Format

### JSON

```json
[
  {
    "source": "harmonic.ai",
    "url": "https://harmonic.ai/...",
    "scraped_at": "2025-11-16T12:00:00",
    "title": "Company Name",
    "description": "Company description...",
    "link": "https://harmonic.ai/company/..."
  }
]
```

### CSV

```csv
source,url,scraped_at,title,description,link
harmonic.ai,https://harmonic.ai/...,2025-11-16T12:00:00,Company Name,Company description...,https://harmonic.ai/company/...
```

## Environment Variables

```bash
# Optional environment configuration
export OUTPUT_DIR=data
export RATE_LIMIT=1.0
export MAX_RETRIES=3
export LOG_LEVEL=INFO
```

## Best Practices

1. **Rate Limiting**: Always use appropriate rate limits to avoid overwhelming the server
2. **Error Handling**: Check crawler logs for errors and adjust retry logic if needed
3. **Data Validation**: Validate extracted data before using in production
4. **Regular Updates**: Site structure may change; update selectors accordingly
5. **Legal Compliance**: Ensure compliance with terms of service and robots.txt

## Troubleshooting

### Common Issues

**No data collected**
- Check if the site structure has changed
- Verify network connectivity
- Review crawler logs for errors

**Rate limiting errors**
- Increase `rate_limit` parameter
- Reduce concurrent requests

**Timeout errors**
- Increase `timeout` parameter
- Check network stability

## Contributing

1. Install development dependencies: `make install`
2. Make changes and add tests
3. Run validation: `make validate`
4. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review test files for usage examples
- Open an issue in the project repository
