# Contributing to General Data Collector

Thank you for your interest in contributing to the General Data Collector project!

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow ethical scraping practices

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create an issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create an issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered
   - Impact and benefits

### Adding New Crawlers

To add a new crawler to the project:

1. **Use the Generator**
   ```bash
   # Edit generate_crawlers.py to add your crawler
   # Add entry to CRAWLERS list:
   {
       "url": "https://example.com",
       "category": "Category Name",
       "description": "Brief description"
   }
   # Run the generator
   python generate_crawlers.py
   ```

2. **Customize the Crawler**
   - Update `crawler.py` with site-specific parsing logic
   - Modify CSS selectors in `parse_page()` method
   - Add any special handling needed

3. **Update Tests**
   - Add tests for your parsing logic
   - Include sample HTML fixtures
   - Test edge cases

4. **Documentation**
   - Update README.md with crawler details
   - Document any special requirements
   - Add usage examples

### Pull Request Process

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/general-data-collector.git
   cd general-data-collector
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add/update tests
   - Update documentation

4. **Run Tests**
   ```bash
   # For specific crawler
   cd crawlers/your_crawler
   make test

   # For all crawlers
   cd ../..
   make test-all
   ```

5. **Run Code Quality Checks**
   ```bash
   # Format code
   make format-all

   # Run linters
   make lint-all

   # Full validation
   make validate-all
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add XYZ crawler" -m "Detailed description..."
   ```

7. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## Commit Message Guidelines

Follow conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

Examples:
```
feat: add HackerNews crawler
fix: correct rate limiting in crunchbase crawler
docs: update README with new examples
test: add tests for error handling
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

```python
# Good
async def fetch(self, url: str, retries: int = 0) -> Optional[str]:
    """Fetch a URL with retry logic."""
    pass

# Bad
def fetch(self,url,retries=0):
    pass
```

### Documentation

- Use docstrings for all public functions/classes
- Include type information
- Provide examples where helpful

```python
def parse_page(self, html: str, url: str) -> List[Dict[str, Any]]:
    """
    Parse HTML content and extract data.

    Args:
        html: HTML content
        url: Source URL

    Returns:
        List of extracted data items

    Example:
        >>> html = "<html>...</html>"
        >>> items = crawler.parse_page(html, "https://example.com")
        >>> len(items)
        10
    """
```

## Testing Guidelines

### Unit Tests

- Test all public methods
- Use mocks for external dependencies
- Test edge cases and error conditions
- Aim for >80% code coverage

```python
async def test_fetch_success(self, crawler):
    """Test successful fetch."""
    await crawler.start()

    with patch.object(crawler.session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>Test</html>")
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await crawler.fetch("https://example.com/test")
        assert result == "<html>Test</html>"

    await crawler.close()
```

### Integration Tests

- Test full crawl workflows
- Verify data export
- Test error recovery

## Ethical Scraping Guidelines

When contributing crawlers, ensure:

1. **Rate Limiting**
   - Default: 1 request/second minimum
   - Configurable via parameters
   - Respect server resources

2. **User-Agent**
   - Clear identification
   - Contact information
   - Purpose description

3. **robots.txt**
   - Check and respect rules
   - Document any exceptions
   - Implement crawl-delay

4. **Terms of Service**
   - Review site ToS
   - Document any restrictions
   - Note legal considerations

5. **Data Handling**
   - No PII collection without consent
   - Respect copyright
   - Proper attribution

## Project Structure

```
general-data-collector/
├── crawlers/               # Crawler modules
│   └── crawler_name/
│       ├── crawler.py      # Main implementation
│       ├── tests/          # Test suite
│       ├── README.md       # Documentation
│       └── ...
├── Makefile               # Build commands
├── docker-compose.yml     # Orchestration
└── generate_crawlers.py   # Generator script
```

## Development Setup

```bash
# Install dependencies
make install-all

# Run tests
make test-all

# Format code
make format-all

# Run linters
make lint-all

# Full CI pipeline
make ci
```

## Docker Development

```bash
# Build image
make docker-build-crawler_name

# Run tests in Docker
make docker-test-crawler_name

# Run crawler in Docker
make docker-run-crawler_name
```

## Adding Dependencies

Update `pyproject.toml`:

```toml
[project]
dependencies = [
    "aiohttp>=3.9.0",
    "beautifulsoup4>=4.12.0",
    "your-new-dependency>=1.0.0",  # Add here
]
```

Then:
```bash
cd crawlers/your_crawler
make install
```

## Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for technical changes
- Add docstrings for new code
- Include usage examples

## Review Process

PRs will be reviewed for:

1. **Code Quality**
   - Follows style guidelines
   - Properly documented
   - Tests included

2. **Functionality**
   - Works as intended
   - Handles errors gracefully
   - Performs efficiently

3. **Ethics**
   - Respects rate limits
   - Follows scraping best practices
   - Complies with ToS

4. **Documentation**
   - Clear and complete
   - Examples provided
   - Architecture documented

## Getting Help

- Check existing issues and PRs
- Read documentation (README, ARCHITECTURE)
- Review similar crawlers
- Ask questions in issues

## Recognition

Contributors will be:
- Added to AUTHORS file
- Credited in release notes
- Mentioned in relevant documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions
- Reach out to maintainers

Thank you for contributing to General Data Collector!
