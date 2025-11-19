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
        timeout: int = 30,
        debug_html: bool = False
    ):
        """
        Initialize the crawler.

        Args:
            output_dir: Directory to save crawled data
            rate_limit: Minimum seconds between requests
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            debug_html: Save raw HTML files for debugging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir = self.output_dir / "debug"
        if debug_html:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self.debug_html = debug_html
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

        # Target the specific container div that holds today's launches
        # XPath: //div[@class='pb-4 w-full']
        container = soup.find('div', class_='pb-4 w-full')

        if not container:
            # Fallback: try variations of the class
            container = soup.find('div', class_='pb-4')
            if not container:
                logger.warning("Could not find container div with class 'pb-4 w-full'")
                container = soup  # Search entire document as fallback
            else:
                logger.info("Found container div with class 'pb-4' (partial match)")
        else:
            logger.info("Found container div with class 'pb-4 w-full'")

        # Find all links containing /tool/ within the container
        all_links = container.find_all('a', href=True)
        logger.info(f"Total links found in container: {len(all_links)}")

        for link in all_links:
            href = link['href']
            # Look for links containing /tool/
            if '/tool/' in href:
                # Handle both absolute and relative URLs
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(url, href)

                # Remove duplicates, fragments, and query parameters
                clean_url = full_url.split('#')[0].split('?')[0]
                if clean_url not in tool_links:
                    tool_links.append(clean_url)
                    logger.debug(f"Found tool link: {clean_url}")

        logger.info(f"Found {len(tool_links)} unique tool links")

        # If no tools found, log some sample links for debugging
        if len(tool_links) == 0:
            logger.warning("No tool links found. Sample links from container:")
            for i, link in enumerate(all_links[:10]):
                logger.warning(f"  Sample link {i+1}: {link.get('href', 'NO HREF')}")

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

        # Extract tool name (h1 or main heading) - try multiple selectors
        name_selectors = [
            'h1',
            '[class*="tool"] h1',
            '[class*="product"] h1',
            '[class*="title"]',
            '.tool-name',
            '.product-name',
            '[data-testid*="title"]',
            '[data-testid*="name"]'
        ]
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                name_text = name_elem.get_text(strip=True)
                if name_text and len(name_text) > 0:
                    data['tool_name'] = name_text
                    logger.debug(f"Found tool name: {name_text}")
                    break

        # Extract overview/description - try multiple approaches
        description_selectors = [
            '[class*="description"]',
            '[class*="overview"]',
            '[class*="about"]',
            '[class*="summary"]',
            'meta[name="description"]',
            'meta[property="og:description"]',
            '.lead',
            'article p',
            'main p'
        ]
        for selector in description_selectors:
            if selector.startswith('meta'):
                desc_elem = soup.select_one(selector)
                if desc_elem and desc_elem.get('content'):
                    data['overview'] = desc_elem['content']
                    logger.debug(f"Found description from meta: {desc_elem['content'][:50]}...")
                    break
            else:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if desc_text and len(desc_text) > 20:  # Avoid short snippets
                        data['overview'] = desc_text
                        logger.debug(f"Found description: {desc_text[:50]}...")
                        break

        # Extract website URL - look for external links
        website_selectors = [
            'a[class*="website"]',
            'a[class*="visit"]',
            'a[class*="external"]',
            'a[href*="http"]:not([href*="uneed.best"]):not([href*="twitter"]):not([href*="linkedin"]):not([href*="facebook"]):not([href*="instagram"])'
        ]
        for selector in website_selectors:
            website_elem = soup.select_one(selector)
            if website_elem and website_elem.get('href'):
                href = website_elem['href']
                # Filter out social media and uneed.best links
                if not any(domain in href for domain in ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'uneed.best', 'youtube.com']):
                    data['website'] = href
                    logger.debug(f"Found website: {href}")
                    break

        # Extract publisher/maker information
        publisher_selectors = [
            '[class*="publisher"]',
            '[class*="maker"]',
            '[class*="creator"]',
            '[class*="author"]',
            '[class*="submitter"]',
            'a[href*="/user/"]',
            'a[href*="/profile/"]'
        ]
        for selector in publisher_selectors:
            publisher_elem = soup.select_one(selector)
            if publisher_elem:
                publisher_name = publisher_elem.get_text(strip=True)
                if publisher_name and len(publisher_name) > 0:
                    data['publisher_name'] = publisher_name
                    logger.debug(f"Found publisher: {publisher_name}")

                    # Try to find publisher link
                    if publisher_elem.name == 'a':
                        data['publisher_link'] = urljoin(tool_url, publisher_elem.get('href', ''))
                    else:
                        publisher_link_elem = publisher_elem.find('a', href=True)
                        if publisher_link_elem:
                            data['publisher_link'] = urljoin(tool_url, publisher_link_elem['href'])
                    break

        # Extract launch date
        date_selectors = [
            'time',
            '[class*="date"]',
            '[class*="launch"]',
            '[datetime]'
        ]
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                # Try datetime attribute first
                if date_elem.get('datetime'):
                    data['launch_date'] = date_elem['datetime']
                    logger.debug(f"Found launch date: {date_elem['datetime']}")
                    break
                else:
                    date_text = date_elem.get_text(strip=True)
                    if date_text:
                        data['launch_date'] = date_text
                        logger.debug(f"Found launch date: {date_text}")
                        break

        # Extract category/tags
        category_selectors = [
            '[class*="category"]',
            '[class*="tag"]',
            '[class*="label"]',
            'a[href*="/category/"]',
            'a[href*="/tag/"]'
        ]
        categories = []
        for selector in category_selectors:
            for cat_elem in soup.select(selector):
                cat_text = cat_elem.get_text(strip=True)
                if cat_text and cat_text not in categories:
                    categories.append(cat_text)

        if categories:
            data['category'] = ', '.join(categories) if len(categories) > 1 else categories[0]
            logger.debug(f"Found categories: {data['category']}")

        # Extract pricing
        pricing_selectors = [
            '[class*="price"]',
            '[class*="pricing"]',
            '[class*="cost"]',
            '[class*="plan"]'
        ]
        for selector in pricing_selectors:
            pricing_elem = soup.select_one(selector)
            if pricing_elem:
                pricing_text = pricing_elem.get_text(strip=True)
                if pricing_text:
                    data['pricing'] = pricing_text
                    logger.debug(f"Found pricing: {pricing_text}")
                    break

        # Extract social links
        socials = {}
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'twitter.com' in href or 'x.com' in href:
                if 'twitter' not in socials:
                    socials['twitter'] = href
            elif 'linkedin.com' in href:
                if 'linkedin' not in socials:
                    socials['linkedin'] = href
            elif 'facebook.com' in href:
                if 'facebook' not in socials:
                    socials['facebook'] = href
            elif 'instagram.com' in href:
                if 'instagram' not in socials:
                    socials['instagram'] = href
            elif 'github.com' in href:
                if 'github' not in socials:
                    socials['github'] = href
            elif 'youtube.com' in href or 'youtu.be' in href:
                if 'youtube' not in socials:
                    socials['youtube'] = href

        if socials:
            data['socials'] = socials
            logger.debug(f"Found {len(socials)} social links")

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

        # Remove None and empty values
        data = {k: v for k, v in data.items() if v is not None and v != ''}

        # Log what fields were extracted
        extracted_fields = [k for k in data.keys() if k not in ['source', 'scraped_at', 'tool_url']]
        logger.info(f"Extracted {len(extracted_fields)} fields for tool: {data.get('tool_name', 'Unknown')} - Fields: {', '.join(extracted_fields)}")

        # Warn if we got minimal data
        if len(extracted_fields) < 2:
            logger.warning(f"Very little data extracted for {tool_url}. Only got: {extracted_fields}")

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
            # Save tool page HTML for debugging (first 3 only to avoid clutter)
            if self.debug_html and len(self.data) < 3:
                tool_slug = tool_url.split('/')[-1]
                tool_page_file = self.debug_dir / f"tool_{tool_slug}.html"
                with open(tool_page_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info(f"Saved tool page HTML to: {tool_page_file}")

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

        # Save main page HTML for debugging
        if self.debug_html:
            main_page_file = self.debug_dir / "main_page.html"
            with open(main_page_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved main page HTML to: {main_page_file}")

        # Extract tool links
        tool_links = self.parse_main_page(html, url)

        if not tool_links:
            logger.error("No tool links found on main page. Check HTML structure or selectors.")
            return []

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
    # Enable DEBUG logging for detailed output
    import sys
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('data/uneed/crawler.log', mode='w')
        ]
    )

    async with UneedCrawler(rate_limit=2.0, debug_html=True) as crawler:
        await crawler.crawl()

        if crawler.data:
            json_file = crawler.save_json()

            print(f"\n{'='*60}")
            print(f"✓ Successfully crawled {len(crawler.data)} tools")
            print(f"{'='*60}")
            print(f"JSON output: {json_file}")
            print(f"Log file: data/uneed/crawler.log")
            print(f"Debug HTML: data/uneed/debug/")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("\n" + "="*60)
            print("No data collected")
            print("="*60)
            print("\nCheck the log file for details: data/uneed/crawler.log")
            print("Check debug HTML files in: data/uneed/debug/")


if __name__ == "__main__":
    asyncio.run(main())
