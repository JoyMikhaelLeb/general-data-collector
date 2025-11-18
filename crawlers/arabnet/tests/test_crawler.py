"""
Tests for arabnet crawler.
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler import ArabnetCrawler


@pytest.fixture
def crawler():
    """Create a crawler instance for testing."""
    return ArabnetCrawler(output_dir="test_data", rate_limit=0.1)


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
        </body>
    </html>
    """


class TestArabnetCrawler:
    """Test suite for ArabnetCrawler."""

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
        async with ArabnetCrawler() as crawler:
            assert crawler.session is not None

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

    def test_parse_page(self, crawler, sample_html):
        """Test HTML parsing."""
        items = crawler.parse_page(sample_html, "https://example.com/test")
        assert isinstance(items, list)

    def test_save_json(self, crawler, tmp_path):
        """Test JSON export."""
        crawler.output_dir = tmp_path
        crawler.data = [{'title': 'Test', 'description': 'Test desc'}]

        filepath = crawler.save_json("test.json")

        assert filepath.exists()
        with open(filepath) as f:
            data = json.load(f)
        assert len(data) == 1

    def test_save_csv(self, crawler, tmp_path):
        """Test CSV export."""
        import csv

        crawler.output_dir = tmp_path
        crawler.data = [{'title': 'Test', 'description': 'Test desc'}]

        filepath = crawler.save_csv("test.csv")
        assert filepath.exists()
