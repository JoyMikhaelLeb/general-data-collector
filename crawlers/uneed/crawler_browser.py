"""
Uneed.best Web Crawler with Browser Support

This version uses Playwright to render JavaScript and get the actual content.
Use this when the regular crawler returns 0 results.

Usage:
    python3 crawler_browser.py

Output: data/uneed/uneed_TIMESTAMP.json
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UneedBrowserCrawler:
    """
    Browser-based crawler for uneed.best using Playwright.

    This crawler uses a real browser to render JavaScript and get
    dynamically loaded content.
    """

    BASE_URL = "https://www.uneed.best"

    def __init__(
        self,
        output_dir: str = "data/uneed",
        rate_limit: float = 2.0,
        headless: bool = True,
        debug_html: bool = False
    ):
        """
        Initialize the browser crawler.

        Args:
            output_dir: Directory to save crawled data
            rate_limit: Minimum seconds between requests
            headless: Run browser in headless mode (False = visible browser)
            debug_html: Save raw HTML files for debugging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir = self.output_dir / "debug"
        if debug_html:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.headless = headless
        self.debug_html = debug_html
        self.browser: Optional[Browser] = None
        self.data: List[Dict[str, Any]] = []

    async def start(self):
        """Initialize the browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info(f"Browser started (headless={self.headless})")

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def fetch_page(self, url: str, wait_for_selector: Optional[str] = None) -> Optional[str]:
        """
        Fetch a page and wait for JavaScript to render.

        Args:
            url: URL to fetch
            wait_for_selector: Optional CSS selector to wait for before getting HTML

        Returns:
            Rendered HTML or None if failed
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Use async context manager.")

        try:
            page = await self.browser.new_page()

            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until='networkidle')

            # Wait for specific selector if provided
            if wait_for_selector:
                logger.info(f"Waiting for selector: {wait_for_selector}")
                await page.wait_for_selector(wait_for_selector, timeout=10000)
            else:
                # Default: wait a bit for dynamic content to load
                await page.wait_for_timeout(2000)

            html = await page.content()
            await page.close()

            logger.info(f"Successfully fetched and rendered: {url}")
            await asyncio.sleep(self.rate_limit)

            return html

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_main_page(self, html: str, url: str) -> List[str]:
        """
        Parse main page and extract tool links.

        Args:
            html: Rendered HTML content
            url: Source URL

        Returns:
            List of tool URLs (/tool/...)
        """
        soup = BeautifulSoup(html, 'html.parser')
        tool_links = []

        logger.info("Parsing rendered HTML for tool links...")

        # Method 1: Look for anchors with specific class
        anchors_with_class = soup.find_all('a', class_=lambda x: x and 'group' in x and 'relative' in x)
        logger.info(f"Found {len(anchors_with_class)} anchors with 'group' and 'relative' classes")

        for anchor in anchors_with_class:
            href = anchor.get('href', '')
            if '/tool/' in href:
                full_url = urljoin(url, href)
                clean_url = full_url.split('#')[0].split('?')[0]
                if clean_url not in tool_links:
                    tool_links.append(clean_url)
                    logger.debug(f"Found tool link: {clean_url}")

        # Method 2: Just search for any link with /tool/
        if not tool_links:
            logger.warning("Method 1 found nothing. Trying to find any links with /tool/...")
            all_tool_links = soup.find_all('a', href=lambda x: x and '/tool/' in x)
            logger.info(f"Found {len(all_tool_links)} links with /tool/ in href")

            for link in all_tool_links:
                href = link.get('href', '')
                full_url = urljoin(url, href)
                clean_url = full_url.split('#')[0].split('?')[0]
                if clean_url not in tool_links:
                    tool_links.append(clean_url)

        logger.info(f"✓ Found {len(tool_links)} unique tool links")

        # Debug info if nothing found
        if not tool_links:
            logger.error("="*60)
            logger.error("NO TOOL LINKS FOUND IN RENDERED HTML")
            logger.error("="*60)
            all_anchors = soup.find_all('a', href=True)
            logger.error(f"Total anchors: {len(all_anchors)}")
            logger.error("Sample anchors:")
            for i, a in enumerate(all_anchors[:10], 1):
                logger.error(f"  [{i}] {a.get('href', 'NO HREF')}")
            logger.error("="*60)

        return tool_links

    def parse_tool_page(self, html: str, tool_url: str) -> Dict[str, Any]:
        """
        Parse tool detail page and extract information.

        Uses the same parsing logic as the original crawler.
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'source': 'uneed_best',
            'scraped_at': datetime.utcnow().isoformat(),
            'tool_url': tool_url,
        }

        # Extract tool name
        name_elem = soup.select_one('h1')
        if name_elem:
            data['tool_name'] = name_elem.get_text(strip=True)

        # Extract description from meta tag
        desc_elem = soup.select_one('meta[property="og:description"]')
        if desc_elem:
            data['overview'] = desc_elem.get('content', '')

        # Extract other fields (simplified for now)
        logger.debug(f"Parsed tool: {data.get('tool_name', 'Unknown')}")
        return data

    async def crawl(self, start_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Main crawl method using browser.

        Args:
            start_url: Starting URL (defaults to BASE_URL)

        Returns:
            List of crawled tool data
        """
        url = start_url or self.BASE_URL

        logger.info(f"Starting browser crawl from: {url}")

        # Fetch and render main page
        # Wait for tool links to appear
        html = await self.fetch_page(url, wait_for_selector='a[href*="/tool/"]')

        if not html:
            logger.error("Failed to fetch main page")
            return []

        # Save rendered HTML for debugging
        if self.debug_html:
            main_page_file = self.debug_dir / "main_page_rendered.html"
            with open(main_page_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved rendered HTML to: {main_page_file}")

        # Extract tool links from rendered page
        tool_links = self.parse_main_page(html, url)

        if not tool_links:
            logger.error("No tool links found in rendered page")
            return []

        logger.info(f"Found {len(tool_links)} tools to scrape")

        # Fetch details for each tool
        for i, tool_url in enumerate(tool_links, 1):
            logger.info(f"Processing tool {i}/{len(tool_links)}: {tool_url}")

            tool_html = await self.fetch_page(tool_url)
            if tool_html:
                tool_data = self.parse_tool_page(tool_html, tool_url)
                self.data.append(tool_data)
            else:
                logger.warning(f"Failed to fetch: {tool_url}")

        logger.info(f"✓ Collected {len(self.data)} tools")
        return self.data

    def save_json(self, filename: Optional[str] = None) -> Path:
        """Save data as JSON."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uneed_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.data)} items to {filepath}")
        return filepath


async def main():
    """Example usage of the browser crawler."""
    import sys
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data/uneed/crawler_browser.log', mode='w')
        ]
    )

    # Set headless=False to see the browser
    async with UneedBrowserCrawler(headless=False, debug_html=True) as crawler:
        await crawler.crawl()

        if crawler.data:
            json_file = crawler.save_json()

            print(f"\n{'='*60}")
            print(f"✓ Successfully crawled {len(crawler.data)} tools")
            print(f"{'='*60}")
            print(f"JSON output: {json_file}")
            print(f"Log file: data/uneed/crawler_browser.log")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("\n" + "="*60)
            print("No data collected")
            print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
