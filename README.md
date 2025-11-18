# General Data Collector

A comprehensive collection of production-ready web crawlers for extracting startup, company, and business data from multiple sources.

## Overview

This project provides 22 specialized web crawlers for collecting data from various startup databases, business registries, investment platforms, and news sources. Each crawler is fully containerized, tested, and production-ready.

## Features

- **22 Specialized Crawlers** - Each targeting a specific data source
- **Asynchronous Architecture** - Built with `asyncio` and `aiohttp` for high performance
- **Docker Support** - Every crawler is fully containerized
- **Comprehensive Testing** - Unit tests with pytest for all crawlers
- **Rate Limiting** - Ethical scraping with configurable delays
- **Multiple Export Formats** - JSON and CSV output
- **Production Ready** - Logging, error handling, and monitoring built-in
- **uv Package Manager** - Fast, reliable dependency management
- **Orchestration** - Docker Compose for running multiple crawlers

## Project Structure

```
general-data-collector/
├── crawlers/                    # Individual crawler modules
│   ├── harmonic_ai/            # Harmonic.ai crawler
│   ├── crunchbase/             # Crunchbase crawler
│   ├── startupstash/           # StartupStash crawler
│   ├── growjo/                 # Growjo crawler
│   ├── betalist/               # BetaList crawler
│   ├── angellist/              # AngelList crawler
│   ├── infogreffe/             # Infogreffe (FR) crawler
│   ├── companies_house/        # Companies House (UK) crawler
│   ├── opencorporates/         # OpenCorporates crawler
│   ├── sec_edgar/              # SEC EDGAR crawler
│   ├── sec_data/               # SEC Data API crawler
│   ├── f6s/                    # F6S crawler
│   ├── betapage/               # BetaPage crawler
│   ├── launched/               # Launched.io crawler
│   ├── magnitt/                # Magnitt (MENA) crawler
│   ├── wamda/                  # Wamda (MENA) crawler
│   ├── startupbahrain/         # Startup Bahrain crawler
│   ├── arabnet/                # ArabNet crawler
│   ├── wellfound/              # Wellfound crawler
│   ├── ventureradar/           # VentureRadar crawler
│   ├── techcrunch_startups/    # TechCrunch Startups crawler
│   └── airtable/               # Airtable public bases crawler
├── data/                       # Output directory (created at runtime)
├── Makefile                    # Master orchestration makefile
├── docker-compose.yml          # Docker orchestration
├── generate_crawlers.py        # Crawler generator script
└── README.md                   # This file
```

Each crawler directory contains:
```
crawler_name/
├── crawler.py           # Main crawler implementation
├── pyproject.toml       # Dependencies (uv compatible)
├── Makefile            # Build and test commands
├── Dockerfile          # Container definition
├── .dockerignore       # Docker exclusions
├── README.md           # Crawler-specific documentation
├── ARCHITECTURE.md     # Technical architecture
└── tests/
    └── test_crawler.py # Test suite
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Docker (optional, for containerized deployment)
- Make

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd general-data-collector

# Install all crawler dependencies
make install-all

# Or install specific crawler
make install-harmonic_ai
```

### Running a Single Crawler

```bash
# Run specific crawler
make run-harmonic_ai

# Or navigate to crawler directory
cd crawlers/harmonic_ai
python crawler.py
```

### Running All Crawlers with Docker Compose

```bash
# Build all images
make docker-compose-build

# Run all crawlers
make docker-compose-up

# Run in background
make docker-compose-up-d

# View logs
make docker-compose-logs

# Stop all crawlers
make docker-compose-down
```

## Available Crawlers

### General Data Collectors
- **harmonic_ai** - Harmonic.ai platform data
- **crunchbase** - Startup and company database
- **startupstash** - Curated startup tools directory
- **growjo** - Fastest-growing companies database
- **betalist** - Early-stage startup discovery
- **angellist** - Startup and investor platform

### Government/Business Registries
- **infogreffe** - French business registry (RCS)
- **companies_house** - UK companies registry
- **opencorporates** - Global company database
- **sec_edgar** - SEC EDGAR filings
- **sec_data** - SEC structured data API

### Startup Databases & Directories
- **f6s** - Global startup community
- **betapage** - New startup discovery
- **launched** - Product launch platform

### Regional/MENA Specific
- **magnitt** - MENA startup platform
- **wamda** - MENA entrepreneurship platform
- **startupbahrain** - Bahrain startup ecosystem
- **arabnet** - MENA digital events

### Funding & Investment Data
- **wellfound** - Startup jobs and recruiting
- **ventureradar** - Market intelligence

### News & Content Platforms
- **techcrunch_startups** - Startup news

### Public Data
- **airtable** - Public Airtable bases

## Development

### Testing

```bash
# Run tests for all crawlers
make test-all

# Run tests for specific crawler
make test-harmonic_ai

# Run tests in Docker
make docker-test-harmonic_ai
```

### Code Quality

```bash
# Format all code
make format-all

# Lint all code
make lint-all

# Validate everything (lint + test)
make validate-all
```

### Building Docker Images

```bash
# Build all images
make docker-build-all

# Build specific image
make docker-build-harmonic_ai

# Run specific crawler in Docker
make docker-run-harmonic_ai
```

## Common Makefile Targets

```bash
make help                    # Show all available commands
make list                    # List all crawlers
make stats                   # Show project statistics
make install-all            # Install all dependencies
make test-all               # Run all tests
make clean-all              # Clean all build artifacts
make docker-build-all       # Build all Docker images
make docker-compose-up      # Start all crawlers
make dev-setup              # Setup development environment
make ci                     # Run full CI pipeline
```

## Output Data

All crawlers save data in both JSON and CSV formats:

```
data/
├── harmonic_ai/
│   ├── harmonic_ai_20251116_120000.json
│   └── harmonic_ai_20251116_120000.csv
├── crunchbase/
│   ├── crunchbase_20251116_120000.json
│   └── crunchbase_20251116_120000.csv
└── ...
```

### Data Schema

Each crawler produces data with common fields:

```json
{
  "source": "crawler_name",
  "url": "source_url",
  "scraped_at": "2025-11-16T12:00:00",
  "title": "Company/Item name",
  "description": "Description text",
  "link": "Detail page URL"
}
```

## Configuration

Each crawler can be configured via environment variables or constructor parameters:

```python
from crawler import CrawlerClass

crawler = CrawlerClass(
    output_dir="data",      # Output directory
    rate_limit=1.0,         # Seconds between requests
    max_retries=3,          # Maximum retry attempts
    timeout=30              # Request timeout
)
```

### Environment Variables

```bash
OUTPUT_DIR=/app/data
RATE_LIMIT=1.0
MAX_RETRIES=3
TIMEOUT=30
LOG_LEVEL=INFO
```

## Architecture

### Technology Stack

- **Python 3.11+** - Modern Python with async support
- **aiohttp** - Async HTTP client
- **BeautifulSoup4** - HTML parsing
- **pytest** - Testing framework
- **Docker** - Containerization
- **uv** - Fast Python package manager
- **Make** - Build orchestration

### Design Principles

1. **Asynchronous I/O** - Non-blocking operations for performance
2. **Rate Limiting** - Ethical scraping with delays
3. **Retry Logic** - Exponential backoff for failures
4. **Modularity** - Each crawler is independent
5. **Testing** - Comprehensive test coverage
6. **Documentation** - Detailed README and architecture docs
7. **Production Ready** - Logging, monitoring, error handling

## Best Practices

### Ethical Scraping

1. **Rate Limiting** - Always use appropriate delays (default 1 req/sec)
2. **User-Agent** - Proper identification in requests
3. **Robots.txt** - Respect crawl directives
4. **Terms of Service** - Review and comply with site ToS
5. **Data Usage** - Use data responsibly and legally

### Performance

1. **Async Operations** - Use async/await for I/O
2. **Connection Pooling** - Reuse HTTP connections
3. **Batch Processing** - Process data in batches
4. **Resource Limits** - Monitor memory and CPU usage

### Reliability

1. **Error Handling** - Graceful degradation
2. **Logging** - Comprehensive logging for debugging
3. **Monitoring** - Track success/failure rates
4. **Testing** - Run tests before deployment

## Troubleshooting

### Common Issues

**Crawler returns no data**
- Check if site structure changed
- Verify network connectivity
- Review crawler logs
- Update CSS selectors if needed

**Rate limiting errors (429)**
- Increase `rate_limit` parameter
- Add delays between requests
- Check site's robots.txt

**Docker build failures**
- Ensure uv is installed
- Check Docker daemon is running
- Verify Dockerfile syntax

**Import errors**
- Run `make install` in crawler directory
- Check Python version (3.11+ required)
- Verify virtual environment is activated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run `make validate-all`
6. Submit a pull request

## Testing

All crawlers include comprehensive test suites:

```bash
# Run tests with coverage
cd crawlers/harmonic_ai
make test

# Run fast tests (no coverage)
make test-fast

# Run in Docker
make docker-test
```

## CI/CD

The project includes a CI pipeline:

```bash
# Run full CI locally
make ci

# This runs:
# 1. make dev-setup (install dependencies)
# 2. make lint-all (code quality)
# 3. make test-all (run tests)
```

## Monitoring

Each crawler provides:
- Structured logging
- Request/response tracking
- Error reporting
- Success/failure metrics

View logs:
```bash
# Docker Compose logs
docker-compose logs -f crawler-name

# Individual crawler
docker logs -f crawler-harmonic-ai
```

## Performance

Typical performance metrics:
- **Request Rate**: 1 req/sec per crawler (configurable)
- **Memory**: ~50MB per crawler
- **CPU**: <5% per crawler
- **Concurrency**: 22 crawlers can run simultaneously

## License

MIT License - See individual crawler directories for details

## Support

For issues, questions, or contributions:
1. Check individual crawler README files
2. Review ARCHITECTURE.md files
3. Open an issue in the repository
4. Submit a pull request

## Acknowledgments

This project follows best practices for:
- Ethical web scraping
- Async Python development
- Docker containerization
- Test-driven development

## Roadmap

- [ ] Add scheduler for periodic crawling
- [ ] Implement data deduplication
- [ ] Add database storage option
- [ ] Create web dashboard for monitoring
- [ ] Add GraphQL/REST API
- [ ] Implement ML-based data extraction
- [ ] Add proxy rotation support
- [ ] Create data quality metrics

## Project Statistics

```bash
# View project stats
make stats
```

Example output:
```
Project Statistics:
  Total crawlers: 22
  Total Python files: 88
  Total test files: 22
  Lines of code: 15000+
```

## Data Sources

### General Data Collectors
- https://harmonic.ai/
- https://crunchbase.com
- https://startupstash.com/
- https://growjo.com/
- https://betalist.com/
- https://www.angellist.com/

### Government/Business Registries
- https://www.infogreffe.fr/
- https://www.gov.uk/government/organisations/companies-house
- https://opencorporates.com/
- https://www.sec.gov/edgar
- https://data.sec.gov/

### Startup Databases & Directories
- https://www.f6s.com/
- https://www.betapage.co/
- https://launched.io/

### Regional/MENA Specific
- https://magnitt.com/
- https://wamda.com/
- https://www.startupbahrain.com/
- https://arabnet.me/

### Funding & Investment Data
- https://wellfound.com/
- https://www.ventureradar.com/

### News & Content Platforms
- https://techcrunch.com/startups/

### Public Airtable Bases
- https://airtable.com/ (search for public shared bases)

---

**Built with ❤️ for the data collection community**
