"""
betalist.com Web Crawler

This crawler extracts data from betalist.com.
Discover and get early access to tomorrow's startups

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


class BetalistCrawler:
    """
    Crawler for betalist.com.

    Features:
    - Asynchronous requests for performance
    - Rate limiting to respect server resources
    - Automatic retry with exponential backoff
    - Data validation and cleaning
    - Export to JSON/CSV formats
    """

    BASE_URL = "https://betalist.com/"

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

        # Betalist.com uses article tags for startup listings
        # Look for startup cards/items on the page
        selectors = [
            'article',  # Main article container
            '.startup-card',
            '.startup-item',
            '[class*="startup"]',
            '[data-startup]',
        ]

        found_items = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                found_items = found
                logger.info(f"Found {len(found)} items using selector: {selector}")
                break

        # Fallback: if no specific selectors work, try to find any content blocks
        if not found_items:
            found_items = soup.select('article, .post, .item, [class*="card"]')
            logger.info(f"Using fallback selector, found {len(found_items)} items")

        for item in found_items:
            try:
                # Extract title (try multiple selectors)
                title = (
                    self._extract_text(item, 'h1') or
                    self._extract_text(item, 'h2') or
                    self._extract_text(item, 'h3') or
                    self._extract_text(item, '.title') or
                    self._extract_text(item, '[class*="title"]') or
                    self._extract_text(item, 'a')
                )

                # Extract description
                description = (
                    self._extract_text(item, '.description') or
                    self._extract_text(item, '[class*="description"]') or
                    self._extract_text(item, 'p') or
                    self._extract_text(item, '.excerpt')
                )

                # Extract link
                link = self._extract_link(item, url)

                # Extract additional metadata
                category = self._extract_text(item, '.category, [class*="category"], .tag, [class*="tag"]')
                date = self._extract_text(item, 'time, [datetime], .date, [class*="date"]')

                # Try to find logo/image
                logo = None
                img = item.select_one('img')
                if img:
                    logo = img.get('src') or img.get('data-src')
                    if logo:
                        logo = urljoin(url, logo)

                data = {
                    'source': 'betalist',
                    'url': url,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'title': title,
                    'description': description,
                    'link': link,
                    'category': category,
                    'date': date,
                    'logo': logo,
                }

                # Only add if we have meaningful data (at least title or description)
                if data.get('title') or data.get('description'):
                    # Remove None values for cleaner output
                    data = {k: v for k, v in data.items() if v is not None}
                    items.append(data)
                    logger.debug(f"Extracted item: {title}")

            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue

        logger.info(f"Successfully parsed {len(items)} items from page")
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

    async def crawl(
        self,
        start_url: Optional[str] = None,
        max_pages: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Main crawl method with pagination support.

        Args:
            start_url: Starting URL (defaults to BASE_URL)
            max_pages: Maximum number of pages to crawl

        Returns:
            List of crawled data items
        """
        url = start_url or self.BASE_URL

        logger.info(f"Starting crawl from: {url} (max {max_pages} pages)")

        for page in range(1, max_pages + 1):
            # Construct page URL (betalist uses /startups/page/N format)
            if page == 1:
                page_url = url
            else:
                page_url = f"{url.rstrip('/')}/startups/page/{page}"

            logger.info(f"Crawling page {page}/{max_pages}: {page_url}")

            html = await self.fetch(page_url)
            if html:
                items = self.parse_page(html, page_url)
                self.data.extend(items)
                logger.info(f"Extracted {len(items)} items from page {page}")
            else:
                logger.warning(f"Failed to fetch page {page}, stopping pagination")
                break

        logger.info(f"Total items collected: {len(self.data)}")
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
            filename = f"betalist_{timestamp}.json"

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
            filename = f"betalist_{timestamp}.csv"

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
    # Crawl 5 pages by default, adjust as needed
    max_pages = 5

    async with BetalistCrawler(output_dir="data/betalist", rate_limit=2.0) as crawler:
        await crawler.crawl(max_pages=max_pages)

        if crawler.data:
            json_file = crawler.save_json()
            csv_file = crawler.save_csv()

            print(f"\n{'='*50}")
            print(f"✓ Successfully crawled {len(crawler.data)} startups from {max_pages} pages")
            print(f"{'='*50}")
            print(f"JSON output: {json_file}")
            print(f"CSV output:  {csv_file}")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("No data collected")


if __name__ == "__main__":
    asyncio.run(main())
