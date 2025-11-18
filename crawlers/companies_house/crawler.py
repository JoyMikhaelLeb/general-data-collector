"""
Companies House UK Web Crawler

This crawler searches for UK companies on find-and-update.company-information.service.gov.uk
and extracts basic company information.

Usage:
    python3 crawler.py

Input: companies.txt (one company name per line)
Output: data/companies_house/companies_TIMESTAMP.json
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, quote_plus

import aiohttp
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompaniesHouseCrawler:
    """
    Crawler for UK Companies House website.

    Searches for companies by name and extracts:
    - Company number
    - Company name
    - Company status
    - Incorporation date
    - Registered address
    - Company type
    """

    BASE_URL = "https://find-and-update.company-information.service.gov.uk"
    SEARCH_URL = f"{BASE_URL}/search/companies"

    def __init__(
        self,
        output_dir: str = "data/companies_house",
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
            'Accept-Language': 'en-GB,en;q=0.9',
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

    def parse_search_results(self, html: str, search_query: str) -> List[Dict[str, Any]]:
        """
        Parse search results page to find companies.

        Args:
            html: HTML content
            search_query: Original search query

        Returns:
            List of company data dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # Companies House search results are in <li> elements
        result_items = soup.select('ul#results li, li.type-company')

        logger.info(f"Found {len(result_items)} results for '{search_query}'")

        for item in result_items:
            try:
                # Extract company name
                name_elem = item.select_one('h3.heading-small a, a.govuk-link, h2 a')
                if not name_elem:
                    continue

                company_name = name_elem.get_text(strip=True)
                company_link = name_elem.get('href', '')

                # Extract company number from link (format: /company/12345678)
                company_number = company_link.split('/')[-1] if company_link else None

                # Extract company status
                status_elem = item.select_one('.company-status, [class*="status"]')
                status = status_elem.get_text(strip=True) if status_elem else None

                # Extract address
                address_elem = item.select_one('.company-address, address, [class*="address"]')
                address = address_elem.get_text(strip=True) if address_elem else None

                # Extract incorporation date (if shown)
                inc_date_elem = item.select_one('.company-incorporation-date, [class*="incorporation"]')
                incorporation_date = inc_date_elem.get_text(strip=True) if inc_date_elem else None

                data = {
                    'source': 'companies_house_uk',
                    'search_query': search_query,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'company_number': company_number,
                    'company_name': company_name,
                    'company_status': status,
                    'registered_address': address,
                    'incorporation_date': incorporation_date,
                    'company_link': urljoin(self.BASE_URL, company_link) if company_link else None,
                }

                # Remove None values
                data = {k: v for k, v in data.items() if v is not None}
                results.append(data)
                logger.debug(f"Extracted: {company_name} ({company_number})")

            except Exception as e:
                logger.warning(f"Error parsing search result: {e}")
                continue

        return results

    async def search_company(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for a company by name.

        Args:
            company_name: Company name to search

        Returns:
            List of matching companies
        """
        # Encode search query
        encoded_query = quote_plus(company_name)
        search_url = f"{self.SEARCH_URL}?q={encoded_query}"

        logger.info(f"Searching for: {company_name}")

        html = await self.fetch(search_url)
        if html:
            results = self.parse_search_results(html, company_name)
            return results

        return []

    async def crawl(self, companies: List[str]) -> List[Dict[str, Any]]:
        """
        Main crawl method - searches for multiple companies.

        Args:
            companies: List of company names to search

        Returns:
            List of all found company data
        """
        logger.info(f"Starting crawl for {len(companies)} companies")

        for i, company_name in enumerate(companies, 1):
            logger.info(f"Processing {i}/{len(companies)}: {company_name}")

            results = await self.search_company(company_name)
            self.data.extend(results)

            if results:
                logger.info(f"Found {len(results)} results for '{company_name}'")
            else:
                logger.warning(f"No results found for '{company_name}'")

        logger.info(f"Total companies collected: {len(self.data)}")
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
            filename = f"companies_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.data)} items to {filepath}")
        return filepath


async def main():
    """Example usage of the crawler."""
    # Read companies from input file
    input_file = Path("companies.txt")

    if input_file.exists():
        with open(input_file, 'r', encoding='utf-8') as f:
            companies = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(companies)} companies from {input_file}")
    else:
        # Default list if no input file
        companies = [
            "HSBC Holdings",
            "BP plc",
            "Tesco",
            "Barclays",
            "Vodafone"
        ]
        logger.warning(f"{input_file} not found. Using default company list.")

    async with CompaniesHouseCrawler(rate_limit=2.0) as crawler:
        await crawler.crawl(companies)

        if crawler.data:
            json_file = crawler.save_json()

            print(f"\n{'='*60}")
            print(f"✓ Successfully crawled {len(crawler.data)} company records")
            print(f"{'='*60}")
            print(f"JSON output: {json_file}")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("No data collected")


if __name__ == "__main__":
    asyncio.run(main())
