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
    - Officers (directors, secretaries, etc.) including:
      - Officer name and profile link
      - Role/position
      - Appointment and resignation dates
      - Nationality, occupation, country of residence
      - Service address
    """

    BASE_URL = "https://find-and-update.company-information.service.gov.uk"
    SEARCH_URL = f"{BASE_URL}/search/companies"

    def __init__(
        self,
        output_dir: str = "data/companies_house",
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
            debug_html: Save HTML files for debugging
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

    def parse_officers_page(self, html: str, officers_url: str) -> List[Dict[str, Any]]:
        """
        Parse officers page to extract officer information.

        Args:
            html: HTML content of officers page
            officers_url: URL of the officers page

        Returns:
            List of officer dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        officers = []

        # Try multiple selector patterns for officers
        # Pattern 1: div.appointment (common structure)
        officer_items = soup.select('div.appointment')

        # Pattern 2: Look for list items in appointments
        if not officer_items:
            officer_items = soup.select('#officer-list li, ul.appointments li')

        # Pattern 3: Look for any div containing officer data
        if not officer_items:
            officer_items = soup.select('div[id*="officer"], div[class*="officer"]')

        # Pattern 4: Table rows
        if not officer_items:
            officer_items = soup.select('table.appointments tbody tr, table tbody tr')

        # Pattern 5: Generic appointment containers
        if not officer_items:
            officer_items = soup.select('.appointment-1, .appointment-2, .appointment-3')

        logger.info(f"Found {len(officer_items)} officer container elements")

        # Debug: If no officers found, log what we DO find
        if len(officer_items) == 0:
            logger.warning("No officer items found with standard selectors")
            logger.warning(f"Checking page for any links containing '/officers/'...")

            # Check for any officer links on the page
            officer_links = soup.find_all('a', href=lambda x: x and '/officers/' in x)
            logger.warning(f"Found {len(officer_links)} links containing '/officers/'")

            if officer_links:
                logger.warning("Sample officer links found:")
                for link in officer_links[:5]:
                    logger.warning(f"  - {link.get('href')}: {link.get_text(strip=True)[:50]}")

            # Try to find any structured content
            all_divs = soup.find_all('div', limit=10)
            logger.warning(f"Sample divs on page (first 10 class names):")
            for div in all_divs:
                classes = div.get('class', [])
                if classes:
                    logger.warning(f"  - {' '.join(classes)}")

        logger.info(f"Attempting to parse {len(officer_items)} officer entries")

        for item in officer_items:
            try:
                officer_data = {}

                # Extract officer name and link
                name_link = item.select_one('a[href*="/officers/"], a.officer-name, h3 a, .heading-small a')
                if name_link:
                    officer_data['officer_name'] = name_link.get_text(strip=True)
                    officer_link = name_link.get('href', '')
                    if officer_link:
                        officer_data['officer_link'] = urljoin(self.BASE_URL, officer_link)
                else:
                    # Try to find name without link
                    name_elem = item.select_one('.officer-name, h3, strong')
                    if name_elem:
                        officer_data['officer_name'] = name_elem.get_text(strip=True)

                # Skip if no name found
                if not officer_data.get('officer_name'):
                    continue

                # Extract officer role/position
                role_elem = item.select_one('.role, .officer-role, [class*="role"], dd')
                if role_elem:
                    officer_data['role'] = role_elem.get_text(strip=True)

                # Extract appointment date
                appointed_elem = item.select_one('[class*="appointed"], [class*="appointment-date"]')
                if appointed_elem:
                    date_text = appointed_elem.get_text(strip=True)
                    # Clean up text like "Appointed on 12 January 2020"
                    if 'appointed' in date_text.lower():
                        date_text = date_text.lower().replace('appointed on', '').replace('appointed', '').strip()
                    officer_data['appointed_on'] = date_text

                # Extract resignation date if present
                resigned_elem = item.select_one('[class*="resigned"], [class*="resignation-date"]')
                if resigned_elem:
                    date_text = resigned_elem.get_text(strip=True)
                    if 'resigned' in date_text.lower():
                        date_text = date_text.lower().replace('resigned on', '').replace('resigned', '').strip()
                    officer_data['resigned_on'] = date_text

                # Extract nationality if present
                nationality_elem = item.select_one('[class*="nationality"]')
                if nationality_elem:
                    officer_data['nationality'] = nationality_elem.get_text(strip=True)

                # Extract occupation if present
                occupation_elem = item.select_one('[class*="occupation"]')
                if occupation_elem:
                    officer_data['occupation'] = occupation_elem.get_text(strip=True)

                # Extract country of residence
                residence_elem = item.select_one('[class*="country-of-residence"]')
                if residence_elem:
                    officer_data['country_of_residence'] = residence_elem.get_text(strip=True)

                # Extract address (service address)
                address_elem = item.select_one('address, [class*="address"]')
                if address_elem:
                    officer_data['address'] = address_elem.get_text(strip=True)

                # Extract from definition lists (dl/dt/dd)
                dl = item.find('dl')
                if dl:
                    dt_elements = dl.find_all('dt')
                    dd_elements = dl.find_all('dd')

                    for dt, dd in zip(dt_elements, dd_elements):
                        key = dt.get_text(strip=True).lower().replace(' ', '_').replace('-', '_')
                        value = dd.get_text(strip=True)

                        if 'correspondence address' in key or 'service address' in key:
                            officer_data['address'] = value
                        elif 'appointed' in key:
                            officer_data['appointed_on'] = value
                        elif 'resigned' in key:
                            officer_data['resigned_on'] = value
                        elif 'nationality' in key:
                            officer_data['nationality'] = value
                        elif 'occupation' in key:
                            officer_data['occupation'] = value
                        elif 'country' in key and 'residence' in key:
                            officer_data['country_of_residence'] = value
                        elif key and value and key not in officer_data:
                            officer_data[key] = value

                # Only add if we have meaningful data
                if officer_data and len(officer_data) > 1:  # More than just name
                    officers.append(officer_data)
                    logger.debug(f"Extracted officer: {officer_data.get('officer_name')}")

            except Exception as e:
                logger.warning(f"Error parsing officer entry: {e}")
                continue

        return officers

    async def fetch_officers(self, company_url: str) -> List[Dict[str, Any]]:
        """
        Fetch and parse officer information for a company.

        Args:
            company_url: URL of the company profile

        Returns:
            List of officer dictionaries
        """
        # Construct officers URL by appending /officers
        if not company_url.endswith('/'):
            officers_url = f"{company_url}/officers"
        else:
            officers_url = f"{company_url}officers"

        logger.info(f"Fetching officers from: {officers_url}")

        html = await self.fetch(officers_url)
        if not html:
            logger.error(f"Failed to fetch officers page: {officers_url}")
            return []

        # Save officers HTML for debugging
        if self.debug_html:
            company_number = company_url.split('/')[-1]
            officers_file = self.debug_dir / f"officers_{company_number}.html"
            with open(officers_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved officers HTML to: {officers_file}")

        officers = self.parse_officers_page(html, officers_url)

        if not officers:
            logger.warning(f"No officers found on page: {officers_url}")
            logger.warning("This might indicate the page structure has changed or officers are not publicly listed")
            if self.debug_html:
                logger.warning(f"Check the saved HTML file for manual inspection: {officers_file}")

        return officers

    def parse_company_profile(self, html: str, company_url: str, search_query: str) -> Dict[str, Any]:
        """
        Parse company profile page to extract detailed information.

        Args:
            html: HTML content of company profile page
            company_url: URL of the company profile
            search_query: Original search query

        Returns:
            Dictionary with detailed company information
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'source': 'companies_house_uk',
            'search_query': search_query,
            'scraped_at': datetime.utcnow().isoformat(),
            'company_link': company_url,
        }

        # Extract company number from URL
        company_number = company_url.split('/')[-1] if company_url else None
        if company_number:
            data['company_number'] = company_number

        # Extract company name (main heading)
        name_elem = soup.select_one('p.heading-xlarge, h1.heading-xlarge, #company-name')
        if name_elem:
            data['company_name'] = name_elem.get_text(strip=True)

        # Extract all data from definition lists (dl elements)
        # Companies House uses <dl> tags for key-value pairs
        for dl in soup.find_all('dl'):
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')

            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True).lower().replace(' ', '_').replace('-', '_')
                value = dd.get_text(strip=True)

                # Map common fields
                if 'company number' in key:
                    data['company_number'] = value
                elif 'company status' in key or 'status' == key:
                    data['company_status'] = value
                elif 'company type' in key or 'type' == key:
                    data['company_type'] = value
                elif 'incorporated on' in key or 'incorporation' in key:
                    data['incorporation_date'] = value
                elif 'registered office' in key or 'address' in key:
                    data['registered_address'] = value
                elif 'nature of business' in key or 'sic' in key:
                    data['nature_of_business'] = value
                elif 'accounts' in key:
                    data['accounts_info'] = value
                elif 'confirmation statement' in key:
                    data['confirmation_statement'] = value
                elif 'previous' in key and 'name' in key:
                    data['previous_names'] = value
                else:
                    # Store any other fields with their original key
                    data[key] = value

        # Extract registered address (alternative selector)
        if 'registered_address' not in data:
            address_elem = soup.select_one('#content-container address, .address')
            if address_elem:
                data['registered_address'] = address_elem.get_text(strip=True)

        # Extract company status (alternative selector)
        if 'company_status' not in data:
            status_elem = soup.select_one('.status, [class*="company-status"]')
            if status_elem:
                data['company_status'] = status_elem.get_text(strip=True)

        logger.debug(f"Extracted profile data for: {data.get('company_name', 'Unknown')}")
        return data

    async def fetch_company_details(self, company_url: str, search_query: str, fetch_officers: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse detailed company information from profile page.

        Args:
            company_url: URL to company profile page
            search_query: Original search query
            fetch_officers: If True, also fetch officer information

        Returns:
            Dictionary with company details (including officers) or None if failed
        """
        logger.info(f"Fetching company details from: {company_url}")

        html = await self.fetch(company_url)
        if html:
            company_data = self.parse_company_profile(html, company_url, search_query)

            # Fetch officers if requested
            if fetch_officers and company_data:
                officers = await self.fetch_officers(company_url)
                if officers:
                    company_data['officers'] = officers
                    company_data['officer_count'] = len(officers)
                    logger.info(f"Found {len(officers)} officers for {company_data.get('company_name', 'Unknown')}")

            return company_data

        return None

    async def search_company(self, company_name: str, fetch_details: bool = True) -> List[Dict[str, Any]]:
        """
        Search for a company by name and optionally fetch detailed info.

        Args:
            company_name: Company name to search
            fetch_details: If True, fetch full details from company profile page

        Returns:
            List of matching companies with details
        """
        # Encode search query
        encoded_query = quote_plus(company_name)
        search_url = f"{self.SEARCH_URL}?q={encoded_query}"

        logger.info(f"Searching for: {company_name}")

        html = await self.fetch(search_url)
        if not html:
            return []

        # Get search results
        results = self.parse_search_results(html, company_name)

        # If fetch_details is True, get detailed info for first result
        if fetch_details and results:
            first_result = results[0]
            company_url = first_result.get('company_link')

            if company_url:
                detailed_data = await self.fetch_company_details(company_url, company_name)
                if detailed_data:
                    # Return the detailed data instead of search result
                    return [detailed_data]

        return results

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

    async with CompaniesHouseCrawler(rate_limit=2.0, debug_html=True) as crawler:
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
