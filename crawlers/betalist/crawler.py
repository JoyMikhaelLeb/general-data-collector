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
        Parse HTML content and extract data from betalist.com.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            List of extracted data items
        """
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        # Build a map of startup elements to their launch dates
        # Dates appear in divs with class "col-span-full text-3xl..." before groups of startups
        # Example: <div class="col-span-full..."><strong>Today</strong> November 18th</div>
        current_date = None
        date_map = {}

        # Find all elements to identify date headers and startups
        for element in soup.find_all('div'):
            # Check if this is a date header div
            classes = element.get('class', [])
            if 'col-span-full' in classes and 'text-3xl' in classes:
                text = element.get_text(strip=True)
                current_date = self._parse_date(text)
                logger.debug(f"Found date header: {text} -> {current_date}")

            # Check if this is a startup div
            elif element.get('id', '').startswith('startup-'):
                if current_date:
                    date_map[element.get('id')] = current_date

        # Now extract all startups
        found_items = soup.select('div.block[id^="startup-"]')
        logger.info(f"Found {len(found_items)} startup items")

        for item in found_items:
            try:
                # Extract startup ID from div id attribute
                startup_id = item.get('id', '').replace('startup-', '')

                # Title: <a class="... font-medium text-gray-900 ...">SubWatch</a>
                title_elem = item.select_one('a.font-medium')
                title = title_elem.get_text(strip=True) if title_elem else None

                # Description: <a class="block text-gray-500 ...">Never forget a subscription...</a>
                desc_elem = item.select_one('a.text-gray-500, a.dark\\:text-gray-400')
                description = desc_elem.get_text(strip=True) if desc_elem else None

                # Link: extract from title link href
                link = None
                if title_elem and title_elem.get('href'):
                    link = urljoin(url, title_elem['href'])

                # Image: extract from img tag
                logo = None
                img = item.select_one('img')
                if img:
                    # Try src first, then srcset (get first URL from srcset)
                    logo = img.get('src')
                    if not logo and img.get('srcset'):
                        # Extract first URL from srcset
                        srcset = img.get('srcset', '')
                        if srcset:
                            logo = srcset.split()[0]  # Get first URL before space/descriptor
                    if logo:
                        logo = urljoin(url, logo)

                # Get launch date from map
                date_launched = date_map.get(item.get('id'))

                data = {
                    'source': 'betalist',
                    'url': url,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'startup_id': startup_id,
                    'title': title,
                    'description': description,
                    'link': link,
                    'logo': logo,
                    'date_launched': date_launched,
                }

                # Only add if we have meaningful data (at least title or link)
                if data.get('title') or data.get('link'):
                    # Remove None values for cleaner output
                    data = {k: v for k, v in data.items() if v is not None}
                    items.append(data)
                    logger.debug(f"Extracted: {title} (ID: {startup_id}, Date: {date_launched})")

            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue

        logger.info(f"Successfully parsed {len(items)} startup items")
        return items

    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse and normalize date text to DD-MM-YYYY format.

        Handles formats like:
        - "Today November 18th"
        - "Yesterday November 17th"
        - "November 18th"
        """
        from datetime import datetime, timedelta
        import re

        date_text = date_text.strip()
        today = datetime.now()

        # Extract the actual date from formats like "Today November 18th"
        # Use regex to find month and day pattern
        month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d+)'
        match = re.search(month_pattern, date_text.lower())

        if match:
            month_name = match.group(1)
            day = match.group(2).rstrip('stndrh')  # Remove st, nd, rd, th suffixes

            # Construct date string with current year
            year = today.year
            date_string = f"{day} {month_name} {year}"

            try:
                parsed = datetime.strptime(date_string, '%d %B %Y')
                return parsed.strftime('%d-%m-%Y')
            except ValueError:
                pass

        # Fallback: Handle relative dates if no explicit date found
        date_lower = date_text.lower()
        if 'today' in date_lower:
            return today.strftime('%d-%m-%Y')
        elif 'yesterday' in date_lower:
            return (today - timedelta(days=1)).strftime('%d-%m-%Y')

        # Try to parse other date formats
        formats = [
            '%d %B %Y',      # 17 November 2025
            '%B %d, %Y',     # November 17, 2025
            '%d/%m/%Y',      # 17/11/2025
            '%Y-%m-%d',      # 2025-11-17
            '%d-%m-%Y',      # 17-11-2025
        ]

        for fmt in formats:
            try:
                cleaned = date_text.replace(',', '').strip()
                parsed = datetime.strptime(cleaned, fmt)
                return parsed.strftime('%d-%m-%Y')
            except ValueError:
                continue

        # If no format matched, return None
        logger.warning(f"Could not parse date: {date_text}")
        return None

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


async def main():
    """Example usage of the crawler."""
    # Crawl only today's listings (1 page)
    max_pages = 1

    async with BetalistCrawler(output_dir="data/betalist", rate_limit=2.0) as crawler:
        await crawler.crawl(max_pages=max_pages)

        if crawler.data:
            json_file = crawler.save_json()

            print(f"\n{'='*50}")
            print(f"✓ Successfully crawled {len(crawler.data)} startups")
            print(f"{'='*50}")
            print(f"JSON output: {json_file}")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("No data collected")


if __name__ == "__main__":
    asyncio.run(main())
