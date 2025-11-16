"""
arabnet.me Web Crawler

This crawler extracts data from arabnet.me.
Digital and startup events in MENA

It follows ethical scraping practices with rate limiting and proper headers.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArabnetCrawler:
    """
    Crawler for arabnet.me.

    Features:
    - Asynchronous requests for performance
    - Rate limiting to respect server resources
    - Automatic retry with exponential backoff
    - Data validation and cleaning
    - Export to JSON/CSV formats
    """

    BASE_URL = "https://arabnet.me/"

    def __init__(
        self,
        output_dir: str = "data",
        rate_limit: float = 1.0,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize the crawler.

        Args:
            output_dir: Directory to save crawled data
            rate_limit: Minimum seconds between requests
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.data: List[Dict[str, Any]] = []

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize the HTTP session."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; DataCollectorBot/1.0)',
            'Accept': 'text/html,application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
        logger.info("Crawler session started")

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("Crawler session closed")

    async def fetch(
        self,
        url: str,
        retries: int = 0
    ) -> Optional[str]:
        """
        Fetch a URL with retry logic.

        Args:
            url: URL to fetch
            retries: Current retry count

        Returns:
            Response text or None if failed
        """
        if not self.session:
            raise RuntimeError("Session not started. Use async context manager.")

        try:
            await asyncio.sleep(self.rate_limit)

            async with self.session.get(url) as response:
                if response.status == 200:
                    logger.info(f"Successfully fetched: {url}")
                    return await response.text()
                elif response.status == 429:  # Rate limited
                    wait_time = 2 ** retries
                    logger.warning(f"Rate limited. Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    if retries < self.max_retries:
                        return await self.fetch(url, retries + 1)
                else:
                    logger.error(f"HTTP {response.status} for {url}")

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            if retries < self.max_retries:
                return await self.fetch(url, retries + 1)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")

        return None

    def parse_page(self, html: str, url: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content and extract data.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            List of extracted data items
        """
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        # TODO: Customize parsing logic for arabnet.me
        # This is a template that should be adapted to the specific site

        # Look for common company/startup data patterns
        for item in soup.select('[class*="company"], [class*="startup"], [class*="item"]'):
            try:
                data = {
                    'source': 'arabnet',
                    'url': url,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'title': self._extract_text(item, '[class*="title"], h1, h2, h3'),
                    'description': self._extract_text(item, '[class*="description"], p'),
                    'link': self._extract_link(item, url),
                }

                # Only add if we have meaningful data
                if data.get('title') or data.get('description'):
                    items.append(data)

            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue

        return items

    def _extract_text(self, element, selector: str) -> Optional[str]:
        """Extract and clean text from element."""
        try:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        except Exception:
            pass
        return None

    def _extract_link(self, element, base_url: str) -> Optional[str]:
        """Extract and normalize link from element."""
        try:
            link = element.select_one('a')
            if link and link.get('href'):
                return urljoin(base_url, link['href'])
        except Exception:
            pass
        return None

    async def crawl(self, start_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Main crawl method.

        Args:
            start_url: Starting URL (defaults to BASE_URL)

        Returns:
            List of crawled data items
        """
        url = start_url or self.BASE_URL

        logger.info(f"Starting crawl from: {url}")

        html = await self.fetch(url)
        if html:
            items = self.parse_page(html, url)
            self.data.extend(items)
            logger.info(f"Extracted {len(items)} items from {url}")

        return self.data

    def save_json(self, filename: Optional[str] = None) -> Path:
        """
        Save data as JSON.

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arabnet_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.data)} items to {filepath}")
        return filepath

    def save_csv(self, filename: Optional[str] = None) -> Path:
        """
        Save data as CSV.

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        import csv

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arabnet_{timestamp}.csv"

        filepath = self.output_dir / filename

        if not self.data:
            logger.warning("No data to save")
            return filepath

        keys = self.data[0].keys()

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.data)

        logger.info(f"Saved {len(self.data)} items to {filepath}")
        return filepath


async def main():
    """Example usage of the crawler."""
    async with ArabnetCrawler(output_dir="data/arabnet") as crawler:
        await crawler.crawl()

        if crawler.data:
            crawler.save_json()
            crawler.save_csv()
            print(f"Successfully crawled {len(crawler.data)} items")
        else:
            print("No data collected")


if __name__ == "__main__":
    asyncio.run(main())
