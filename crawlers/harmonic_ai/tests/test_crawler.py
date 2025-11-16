"""
Tests for Harmonic.ai crawler.
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler import HarmonicCrawler


@pytest.fixture
def crawler():
    """Create a crawler instance for testing."""
    return HarmonicCrawler(output_dir="test_data", rate_limit=0.1)


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <html>
        <body>
            <div class="company">
                <h2 class="title">Test Company</h2>
                <p class="description">A test company description</p>
                <a href="/company/test">View Details</a>
            </div>
            <div class="company">
                <h2 class="title">Another Company</h2>
                <p class="description">Another description</p>
                <a href="/company/another">View Details</a>
            </div>
        </body>
    </html>
    """


class TestHarmonicCrawler:
    """Test suite for HarmonicCrawler."""

    def test_init(self, crawler):
        """Test crawler initialization."""
        assert crawler.output_dir == Path("test_data")
        assert crawler.rate_limit == 0.1
        assert crawler.max_retries == 3
        assert crawler.data == []

    async def test_start_close(self, crawler):
        """Test session lifecycle."""
        await crawler.start()
        assert crawler.session is not None
        await crawler.close()

    async def test_context_manager(self):
        """Test async context manager."""
        async with HarmonicCrawler() as crawler:
            assert crawler.session is not None
        # Session should be closed after exit

    async def test_fetch_success(self, crawler):
        """Test successful fetch."""
        await crawler.start()

        with patch.object(crawler.session, 'get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html>Test</html>")
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await crawler.fetch("https://harmonic.ai/test")

            assert result == "<html>Test</html>"
            mock_get.assert_called_once()

        await crawler.close()

    async def test_fetch_rate_limit(self, crawler):
        """Test rate limiting handling."""
        await crawler.start()

        with patch.object(crawler.session, 'get') as mock_get:
            # First call returns 429, second call succeeds
            mock_response_429 = AsyncMock()
            mock_response_429.status = 429

            mock_response_200 = AsyncMock()
            mock_response_200.status = 200
            mock_response_200.text = AsyncMock(return_value="<html>Success</html>")

            mock_get.return_value.__aenter__.side_effect = [
                mock_response_429,
                mock_response_200
            ]

            result = await crawler.fetch("https://harmonic.ai/test")

            assert result == "<html>Success</html>"
            assert mock_get.call_count == 2

        await crawler.close()

    async def test_fetch_timeout(self, crawler):
        """Test timeout handling."""
        await crawler.start()

        with patch.object(crawler.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.side_effect = asyncio.TimeoutError()

            result = await crawler.fetch("https://harmonic.ai/test")

            assert result is None

        await crawler.close()

    def test_parse_page(self, crawler, sample_html):
        """Test HTML parsing."""
        items = crawler.parse_page(sample_html, "https://harmonic.ai/test")

        assert len(items) == 2
        assert items[0]['title'] == "Test Company"
        assert items[0]['description'] == "A test company description"
        assert items[0]['source'] == "harmonic.ai"
        assert items[1]['title'] == "Another Company"

    def test_extract_text(self, crawler):
        """Test text extraction."""
        from bs4 import BeautifulSoup

        html = '<div><h1 class="title">Test Title</h1></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')

        text = crawler._extract_text(element, '.title')
        assert text == "Test Title"

    def test_extract_link(self, crawler):
        """Test link extraction."""
        from bs4 import BeautifulSoup

        html = '<div><a href="/test">Link</a></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')

        link = crawler._extract_link(element, "https://harmonic.ai")
        assert link == "https://harmonic.ai/test"

    async def test_crawl(self, crawler, sample_html):
        """Test main crawl method."""
        await crawler.start()

        with patch.object(crawler, 'fetch', return_value=sample_html):
            data = await crawler.crawl()

            assert len(data) == 2
            assert crawler.data == data

        await crawler.close()

    def test_save_json(self, crawler, tmp_path):
        """Test JSON export."""
        crawler.output_dir = tmp_path
        crawler.data = [
            {'title': 'Test', 'description': 'Test desc'},
            {'title': 'Test 2', 'description': 'Test desc 2'},
        ]

        filepath = crawler.save_json("test.json")

        assert filepath.exists()
        with open(filepath) as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]['title'] == 'Test'

    def test_save_csv(self, crawler, tmp_path):
        """Test CSV export."""
        import csv

        crawler.output_dir = tmp_path
        crawler.data = [
            {'title': 'Test', 'description': 'Test desc'},
            {'title': 'Test 2', 'description': 'Test desc 2'},
        ]

        filepath = crawler.save_csv("test.csv")

        assert filepath.exists()
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['title'] == 'Test'

    def test_save_csv_empty(self, crawler, tmp_path):
        """Test CSV export with no data."""
        crawler.output_dir = tmp_path
        crawler.data = []

        filepath = crawler.save_csv("empty.csv")

        # Should not raise an error
        assert filepath == tmp_path / "empty.csv"


@pytest.mark.asyncio
async def test_main_function():
    """Test the main function."""
    with patch('crawler.HarmonicCrawler') as MockCrawler:
        mock_instance = AsyncMock()
        mock_instance.data = [{'test': 'data'}]
        MockCrawler.return_value.__aenter__.return_value = mock_instance

        from crawler import main
        await main()

        mock_instance.crawl.assert_called_once()
        mock_instance.save_json.assert_called_once()
        mock_instance.save_csv.assert_called_once()
