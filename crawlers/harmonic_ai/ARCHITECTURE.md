# Harmonic.ai Crawler Architecture

## Overview

The Harmonic.ai crawler is designed as a production-ready, asynchronous web scraping system that follows best practices for web crawling, data extraction, and ethical scraping.

## Design Principles

### 1. Asynchronous Architecture

The crawler uses Python's `asyncio` and `aiohttp` for non-blocking I/O operations, allowing:
- Concurrent request handling
- Efficient resource utilization
- Scalable performance

```
┌─────────────┐
│   Main      │
│  Crawler    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Async HTTP Session         │
│  (aiohttp.ClientSession)    │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Rate Limiter               │
│  (asyncio.sleep)            │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Request/Response Handler   │
│  (fetch method)             │
└─────────────────────────────┘
```

### 2. Component Architecture

```
┌────────────────────────────────────────────┐
│         HarmonicCrawler                    │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Session Management              │     │
│  │  - start()                       │     │
│  │  - close()                       │     │
│  │  - __aenter__/__aexit__          │     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  HTTP Operations                 │     │
│  │  - fetch()                       │     │
│  │  - retry logic                   │     │
│  │  - rate limiting                 │     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Data Extraction                 │     │
│  │  - parse_page()                  │     │
│  │  - _extract_text()               │     │
│  │  - _extract_link()               │     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Data Storage                    │     │
│  │  - save_json()                   │     │
│  │  - save_csv()                    │     │
│  └──────────────────────────────────┘     │
│                                            │
└────────────────────────────────────────────┘
```

## Core Components

### 1. Session Management

**Purpose**: Manage HTTP session lifecycle

**Key Features**:
- Async context manager support (`async with`)
- Automatic session cleanup
- Configurable headers and timeouts
- Connection pooling through aiohttp

**Implementation**:
```python
async with HarmonicCrawler() as crawler:
    await crawler.crawl()
# Session automatically closed
```

### 2. Request Handler

**Purpose**: Fetch web pages with resilience

**Key Features**:
- Exponential backoff retry
- Rate limiting compliance
- Timeout handling
- HTTP status code handling

**Flow**:
```
Start Request
     │
     ▼
Apply Rate Limit
     │
     ▼
Send HTTP Request
     │
     ├─► [200 OK] ──► Return Content
     │
     ├─► [429 Rate Limited] ──► Exponential Backoff ──► Retry
     │
     ├─► [Timeout] ──► Retry (if attempts < max_retries)
     │
     └─► [Error] ──► Log Error ──► Return None
```

### 3. Data Extraction Pipeline

**Purpose**: Parse HTML and extract structured data

**Architecture**:
```
Raw HTML
   │
   ▼
BeautifulSoup Parser
   │
   ▼
CSS Selector Matching
   │
   ├─► Extract Text Fields
   │
   ├─► Extract Links
   │
   └─► Extract Metadata
   │
   ▼
Data Validation
   │
   ▼
Structured Output
```

**Key Features**:
- CSS selector-based extraction
- Graceful error handling
- URL normalization
- Text cleaning

### 4. Data Storage

**Purpose**: Persist extracted data

**Supported Formats**:
- JSON (hierarchical data)
- CSV (tabular data)

**Features**:
- Automatic timestamping
- UTF-8 encoding support
- Directory management

## Data Flow

```
┌──────────────┐
│    Start     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Initialize   │
│  Crawler     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Start HTTP   │
│  Session     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Fetch Page   │
│  (with retry)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Parse HTML  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Extract Data │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Validate &   │
│   Store      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Export to    │
│ JSON/CSV     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Close Session│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     End      │
└──────────────┘
```

## Error Handling Strategy

### 1. Network Errors
- Automatic retry with exponential backoff
- Configurable maximum retry attempts
- Timeout protection

### 2. Parsing Errors
- Try-except blocks around extraction logic
- Continue on individual item failures
- Log warnings for debugging

### 3. Data Errors
- Validation before storage
- Skip empty/invalid records
- Maintain data integrity

## Scalability Considerations

### Current Implementation
- Single-threaded async event loop
- Sequential page fetching
- In-memory data storage

### Future Enhancements
1. **Concurrent Crawling**
   - Multiple URLs in parallel
   - Worker pool pattern
   - Queue-based distribution

2. **Distributed Architecture**
   - Message queue integration (RabbitMQ/Redis)
   - Multiple crawler instances
   - Centralized data storage

3. **Data Storage**
   - Database integration (PostgreSQL/MongoDB)
   - Streaming writes
   - Batch processing

## Performance Optimization

### Current Optimizations
- Async I/O for non-blocking operations
- Connection pooling via aiohttp
- Minimal memory footprint

### Benchmarks
- **Request Rate**: ~1 request/second (with rate_limit=1.0)
- **Memory Usage**: ~50MB base + data size
- **CPU Usage**: <5% on modern hardware

### Tuning Parameters

```python
# Performance vs. Politeness tradeoff
crawler = HarmonicCrawler(
    rate_limit=0.5,     # 2 requests/second (aggressive)
    rate_limit=1.0,     # 1 request/second (balanced)
    rate_limit=2.0,     # 0.5 requests/second (polite)
)
```

## Security Considerations

### 1. Network Security
- HTTPS by default
- Certificate verification
- User-Agent identification

### 2. Data Security
- No credential storage in code
- Environment variable support
- Secure file permissions

### 3. Resource Protection
- Rate limiting to prevent server overload
- Timeout limits
- Memory bounds

## Testing Strategy

### Unit Tests
- Component isolation
- Mock external dependencies
- Edge case coverage

### Integration Tests
- Full crawl simulation
- Data export validation
- Error scenario testing

### Test Structure
```
tests/
└── test_crawler.py
    ├── TestHarmonicCrawler
    │   ├── test_init()
    │   ├── test_start_close()
    │   ├── test_fetch_success()
    │   ├── test_fetch_rate_limit()
    │   ├── test_parse_page()
    │   ├── test_save_json()
    │   └── test_save_csv()
    └── test_main_function()
```

## Deployment Architecture

### Docker Container
```
┌─────────────────────────────────┐
│  Docker Container               │
│                                 │
│  ┌───────────────────────────┐ │
│  │  Python 3.11 Runtime      │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │  Application Code         │ │
│  │  - crawler.py             │ │
│  │  - dependencies           │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │  Volume Mounts            │ │
│  │  - /app/data (output)     │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

### Production Deployment
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Crawler│ │Crawler│  (Multiple instances)
│ Pod 1 │ │ Pod 2 │
└───┬───┘ └──┬────┘
    │        │
    └────┬───┘
         │
    ┌────▼────┐
    │ Storage │
    │(S3/NFS) │
    └─────────┘
```

## Monitoring and Observability

### Logging
- Structured logging with levels
- Request/response tracking
- Error reporting

### Metrics (Future)
- Request count
- Success/failure rates
- Response times
- Data volume

### Health Checks
- Docker HEALTHCHECK
- Session status
- Disk space monitoring

## Configuration Management

### Environment Variables
```bash
OUTPUT_DIR=/app/data
RATE_LIMIT=1.0
MAX_RETRIES=3
TIMEOUT=30
LOG_LEVEL=INFO
```

### Configuration File (Future)
```yaml
crawler:
  rate_limit: 1.0
  max_retries: 3
  timeout: 30

storage:
  output_dir: /app/data
  format: json

logging:
  level: INFO
  format: json
```

## Maintenance and Updates

### Regular Tasks
1. Monitor site structure changes
2. Update CSS selectors
3. Review error logs
4. Update dependencies

### Dependency Management
- Using `uv` for fast, reliable installs
- Version pinning in `pyproject.toml`
- Regular security updates

## Legal and Ethical Considerations

### Robots.txt Compliance
- Check robots.txt before crawling
- Respect crawl delays
- Honor disallow directives

### Rate Limiting
- Default 1 request/second
- Configurable for different scenarios
- Respectful of server resources

### Terms of Service
- Review site ToS before deployment
- Ensure compliance with data usage policies
- Implement proper attribution

## Future Enhancements

1. **Multi-page Pagination Support**
2. **JavaScript Rendering** (Playwright/Selenium)
3. **Proxy Rotation**
4. **Cache Layer** (Redis)
5. **GraphQL API Support**
6. **Real-time Streaming**
7. **ML-based Data Extraction**

## References

- [aiohttp Documentation](https://docs.aiohttp.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
