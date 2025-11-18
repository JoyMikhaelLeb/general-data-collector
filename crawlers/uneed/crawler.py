"""
Uneed.best Web Crawler

This crawler extracts data from uneed.best - a daily launch platform for new tools.
Discovers new tools and their detailed information.

Usage:
    python3 crawler.py

Output: data/uneed/uneed_TIMESTAMP.json
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UneedCrawler:
    """
    Crawler for uneed.best.

    Extracts daily tool launches with:
    - Tool name and description
    - Website URL
    - Publisher information
    - Launch date
    - Category
    - Pricing
    - Social links
    - For Sale status
    """

    BASE_URL = "https://www.uneed.best"

    def __init__(
        self,
        output_dir: str = "data/uneed",
        rate_limit: float = 2.0,
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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

    async def fetch(self, url: str, retries: int = 0) -> Optional[str]:
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

    def parse_main_page(self, html: str, url: str) -> List[str]:
        """
        Parse main page and extract tool links.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            List of tool URLs (/tool/...)
        """
        soup = BeautifulSoup(html, 'html.parser')
        tool_links = []

        # Find all links containing /tool/
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/tool/' in href:
                full_url = urljoin(url, href)
                if full_url not in tool_links:
                    tool_links.append(full_url)

        logger.info(f"Found {len(tool_links)} tool links")
        return tool_links

    def parse_tool_page(self, html: str, tool_url: str) -> Dict[str, Any]:
        """
        Parse tool detail page and extract all information.

        Args:
            html: HTML content of tool page
            tool_url: URL of the tool page

        Returns:
            Dictionary with tool information
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'source': 'uneed_best',
            'scraped_at': datetime.utcnow().isoformat(),
            'tool_url': tool_url,
        }

        # Extract tool name (h1 or main heading)
        name_elem = soup.select_one('h1, .tool-name, [class*="title"]')
        if name_elem:
            data['tool_name'] = name_elem.get_text(strip=True)

        # Extract overview/description
        # Try multiple possible selectors
        overview_elem = soup.select_one('.overview, .description, [class*="description"], p')
        if overview_elem:
            data['overview'] = overview_elem.get_text(strip=True)

        # Extract website URL
        website_elem = soup.select_one('a[href*="http"]:not([href*="uneed.best"])')
        if website_elem:
            data['website'] = website_elem.get('href')

        # Extract publisher information
        publisher_elem = soup.select_one('.publisher, [class*="publisher"], [class*="maker"]')
        if publisher_elem:
            # Publisher name
            publisher_name = publisher_elem.get_text(strip=True)
            if publisher_name:
                data['publisher_name'] = publisher_name

            # Publisher link
            publisher_link_elem = publisher_elem.find('a', href=True)
            if publisher_link_elem:
                data['publisher_link'] = urljoin(tool_url, publisher_link_elem['href'])

        # Extract launch date
        date_elem = soup.select_one('.launch-date, [class*="date"], time')
        if date_elem:
            data['launch_date'] = date_elem.get_text(strip=True)
            # Also try datetime attribute
            if date_elem.get('datetime'):
                data['launch_date'] = date_elem['datetime']

        # Extract category
        category_elem = soup.select_one('.category, [class*="category"], .tag, [class*="tag"]')
        if category_elem:
            data['category'] = category_elem.get_text(strip=True)

        # Extract pricing
        pricing_elem = soup.select_one('.pricing, [class*="price"], [class*="pricing"]')
        if pricing_elem:
            data['pricing'] = pricing_elem.get_text(strip=True)

        # Extract social links
        socials = {}
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'twitter.com' in href or 'x.com' in href:
                socials['twitter'] = href
            elif 'linkedin.com' in href:
                socials['linkedin'] = href
            elif 'facebook.com' in href:
                socials['facebook'] = href
            elif 'instagram.com' in href:
                socials['instagram'] = href
            elif 'github.com' in href:
                socials['github'] = href
            elif 'youtube.com' in href:
                socials['youtube'] = href

        if socials:
            data['socials'] = socials

        # Extract "For Sale" status
        for_sale_elem = soup.select_one('[class*="for-sale"], [class*="forsale"]')
        if for_sale_elem:
            data['for_sale'] = for_sale_elem.get_text(strip=True)
        else:
            # Check if text "for sale" appears anywhere
            if 'for sale' in html.lower():
                data['for_sale'] = True

        # Try to extract any additional metadata from dl/dt/dd elements
        for dl in soup.find_all('dl'):
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')

            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True).lower().replace(' ', '_').replace('-', '_')
                value = dd.get_text(strip=True)

                if key and value and key not in data:
                    data[key] = value

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        logger.debug(f"Extracted tool: {data.get('tool_name', 'Unknown')}")
        return data

    async def fetch_tool_details(self, tool_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse detailed tool information.

        Args:
            tool_url: URL to tool page

        Returns:
            Dictionary with tool details or None if failed
        """
        logger.info(f"Fetching tool details from: {tool_url}")

        html = await self.fetch(tool_url)
        if html:
            return self.parse_tool_page(html, tool_url)

        return None

    async def crawl(self, start_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Main crawl method.

        Args:
            start_url: Starting URL (defaults to BASE_URL)

        Returns:
            List of crawled tool data
        """
        url = start_url or self.BASE_URL

        logger.info(f"Starting crawl from: {url}")

        # Fetch main page
        html = await self.fetch(url)
        if not html:
            logger.error("Failed to fetch main page")
            return []

        # Extract tool links
        tool_links = self.parse_main_page(html, url)

        # Fetch details for each tool
        for i, tool_url in enumerate(tool_links, 1):
            logger.info(f"Processing tool {i}/{len(tool_links)}: {tool_url}")

            tool_data = await self.fetch_tool_details(tool_url)
            if tool_data:
                self.data.append(tool_data)
            else:
                logger.warning(f"Failed to fetch details for: {tool_url}")

        logger.info(f"Total tools collected: {len(self.data)}")
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
            filename = f"uneed_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.data)} items to {filepath}")
        return filepath


async def main():
    """Example usage of the crawler."""
    async with UneedCrawler(rate_limit=2.0) as crawler:
        await crawler.crawl()

        if crawler.data:
            json_file = crawler.save_json()

            print(f"\n{'='*60}")
            print(f"✓ Successfully crawled {len(crawler.data)} tools")
            print(f"{'='*60}")
            print(f"JSON output: {json_file}")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("No data collected")


if __name__ == "__main__":
    asyncio.run(main())
