"""
Companies House UK Officer Profile Crawler

This crawler extracts detailed information from officer profile pages.

Usage:
    python3 crawler_profiles.py

Input: officer_urls.txt (one officer profile URL per line)
Output: data/companies_house/officers_TIMESTAMP.json
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


class OfficerProfileCrawler:
    """
    Crawler for UK Companies House officer profile pages.

    Extracts detailed officer information including:
    - Full name and date of birth
    - All current and previous appointments
    - Company associations
    - Appointment/resignation dates
    - Roles and positions
    """

    BASE_URL = "https://find-and-update.company-information.service.gov.uk"

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

    def parse_officer_profile(self, html: str, profile_url: str) -> Dict[str, Any]:
        """
        Parse officer profile page to extract detailed information.

        Args:
            html: HTML content of profile page
            profile_url: URL of the profile page

        Returns:
            Dictionary with officer profile information
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'source': 'companies_house_uk',
            'scraped_at': datetime.utcnow().isoformat(),
            'profile_url': profile_url,
        }

        # Extract officer ID from URL
        # Format: /officers/{officer_id}/appointments
        if '/officers/' in profile_url:
            parts = profile_url.split('/officers/')
            if len(parts) > 1:
                officer_id = parts[1].split('/')[0]
                data['officer_id'] = officer_id

        # Extract officer name (main heading)
        name_elem = soup.select_one('h1, .heading-xlarge')
        if name_elem:
            data['officer_name'] = name_elem.get_text(strip=True)

        # Extract date of birth if present
        dob_elem = soup.select_one('[class*="date-of-birth"], [class*="born"]')
        if dob_elem:
            data['date_of_birth'] = dob_elem.get_text(strip=True)

        # Extract nationality
        nationality_elem = soup.select_one('[class*="nationality"]')
        if nationality_elem:
            data['nationality'] = nationality_elem.get_text(strip=True)

        # Extract all appointments (current and previous)
        appointments = []

        # Look for appointment sections
        appointment_sections = soup.select('div.appointment, li.appointment, tr.appointment')

        if not appointment_sections:
            # Try table rows
            appointment_sections = soup.select('table tbody tr')

        logger.info(f"Found {len(appointment_sections)} appointment entries")

        for appt_elem in appointment_sections:
            try:
                appointment = {}

                # Company name and link
                company_link = appt_elem.select_one('a[href*="/company/"]')
                if company_link:
                    appointment['company_name'] = company_link.get_text(strip=True)
                    company_href = company_link.get('href', '')
                    if company_href:
                        appointment['company_link'] = urljoin(self.BASE_URL, company_href)
                        # Extract company number from link
                        if '/company/' in company_href:
                            appointment['company_number'] = company_href.split('/company/')[-1].split('/')[0]

                # Role/position
                role_elem = appt_elem.select_one('[class*="role"], td:nth-of-type(2), .appointment-role')
                if role_elem:
                    appointment['role'] = role_elem.get_text(strip=True)

                # Status (Active/Resigned)
                status_elem = appt_elem.select_one('[class*="status"], .appointment-status')
                if status_elem:
                    appointment['status'] = status_elem.get_text(strip=True)

                # Appointed date
                appointed_elem = appt_elem.select_one('[class*="appointed"], .appointed-on')
                if appointed_elem:
                    date_text = appointed_elem.get_text(strip=True)
                    if 'appointed' in date_text.lower():
                        date_text = date_text.lower().replace('appointed on', '').replace('appointed', '').strip()
                    appointment['appointed_on'] = date_text

                # Resigned date (if applicable)
                resigned_elem = appt_elem.select_one('[class*="resigned"], .resigned-on')
                if resigned_elem:
                    date_text = resigned_elem.get_text(strip=True)
                    if 'resigned' in date_text.lower():
                        date_text = date_text.lower().replace('resigned on', '').replace('resigned', '').strip()
                    appointment['resigned_on'] = date_text

                # Extract from definition lists
                dl = appt_elem.find('dl')
                if dl:
                    dt_elements = dl.find_all('dt')
                    dd_elements = dl.find_all('dd')

                    for dt, dd in zip(dt_elements, dd_elements):
                        key = dt.get_text(strip=True).lower().replace(' ', '_').replace('-', '_')
                        value = dd.get_text(strip=True)

                        if key and value and key not in appointment:
                            appointment[key] = value

                # Only add if we have meaningful data
                if appointment and len(appointment) > 0:
                    appointments.append(appointment)
                    logger.debug(f"Extracted appointment: {appointment.get('company_name', 'Unknown')}")

            except Exception as e:
                logger.warning(f"Error parsing appointment: {e}")
                continue

        if appointments:
            data['appointments'] = appointments
            data['appointment_count'] = len(appointments)

            # Count active vs resigned
            active = sum(1 for a in appointments if a.get('status', '').lower() == 'active' or 'resigned_on' not in a)
            resigned = len(appointments) - active
            data['active_appointments'] = active
            data['resigned_appointments'] = resigned

        # Extract any additional fields from definition lists on main profile
        for dl in soup.find_all('dl'):
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')

            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True).lower().replace(' ', '_').replace('-', '_')
                value = dd.get_text(strip=True)

                if key and value and key not in data:
                    data[key] = value

        logger.info(f"Extracted profile for: {data.get('officer_name', 'Unknown')} with {len(appointments)} appointments")
        return data

    async def fetch_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse officer profile.

        Args:
            profile_url: URL to officer profile page

        Returns:
            Dictionary with profile data or None if failed
        """
        logger.info(f"Fetching profile from: {profile_url}")

        html = await self.fetch(profile_url)
        if not html:
            logger.error(f"Failed to fetch profile: {profile_url}")
            return None

        # Save profile HTML for debugging
        if self.debug_html:
            officer_id = profile_url.split('/')[-2] if '/officers/' in profile_url else 'unknown'
            profile_file = self.debug_dir / f"profile_{officer_id}.html"
            with open(profile_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved profile HTML to: {profile_file}")

        return self.parse_officer_profile(html, profile_url)

    async def crawl(self, profile_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Main crawl method - fetches multiple officer profiles.

        Args:
            profile_urls: List of officer profile URLs to fetch

        Returns:
            List of all officer profile data
        """
        logger.info(f"Starting crawl for {len(profile_urls)} officer profiles")

        for i, profile_url in enumerate(profile_urls, 1):
            logger.info(f"Processing {i}/{len(profile_urls)}: {profile_url}")

            profile_data = await self.fetch_profile(profile_url)
            if profile_data:
                self.data.append(profile_data)
            else:
                logger.warning(f"No data collected for: {profile_url}")

        logger.info(f"Total officer profiles collected: {len(self.data)}")
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
            filename = f"officers_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.data)} items to {filepath}")
        return filepath


async def main():
    """Example usage of the crawler."""
    # Read officer URLs from input file
    input_file = Path("officer_urls.txt")

    if input_file.exists():
        with open(input_file, 'r', encoding='utf-8') as f:
            profile_urls = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(profile_urls)} officer URLs from {input_file}")
    else:
        # Default example URLs if no input file
        profile_urls = [
            "https://find-and-update.company-information.service.gov.uk/officers/abc123xyz/appointments",
            "https://find-and-update.company-information.service.gov.uk/officers/def456uvw/appointments",
        ]
        logger.warning(f"{input_file} not found. Using example URLs.")

    async with OfficerProfileCrawler(rate_limit=2.0, debug_html=True) as crawler:
        await crawler.crawl(profile_urls)

        if crawler.data:
            json_file = crawler.save_json()

            print(f"\n{'='*60}")
            print(f"✓ Successfully crawled {len(crawler.data)} officer profiles")
            print(f"{'='*60}")
            print(f"JSON output: {json_file}")
            print(f"\nSample data (first item):")
            print(json.dumps(crawler.data[0], indent=2))
        else:
            print("No data collected")


if __name__ == "__main__":
    asyncio.run(main())
