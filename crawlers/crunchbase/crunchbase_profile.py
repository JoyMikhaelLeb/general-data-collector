"""
Crunchbase Person Profile Crawler

This crawler logs into Crunchbase and extracts detailed profile information
for people listed in a profiles.txt file.

Features:
- Authenticated login to Crunchbase
- Profile data extraction (overview, links, jobs, education)
- Individual JSON files per profile
- Browser automation with Playwright
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Browser, Page


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrunchbaseProfileCrawler:
    """
    Crawler for Crunchbase person profiles with authentication.

    Extracts comprehensive profile data including:
    - Overview information
    - Social/web links
    - Work experience/jobs
    - Education history
    """

    BASE_URL = "https://www.crunchbase.com"
    LOGIN_URL = "https://www.crunchbase.com/login"

    def __init__(
        self,
        email: str,
        password: str,
        profiles_file: str = "profiles.txt",
        output_dir: str = "data/crunchbase/profiles",
        headless: bool = True,
        debug_html: bool = False,
        rate_limit: float = 2.0
    ):
        """
        Initialize the crawler.

        Args:
            email: Crunchbase account email
            password: Crunchbase account password
            profiles_file: Path to file containing profile names (one per line)
            output_dir: Directory to save JSON files
            headless: Run browser in headless mode
            debug_html: Save HTML files for debugging
            rate_limit: Seconds to wait between profile requests
        """
        self.email = email
        self.password = password
        self.profiles_file = Path(profiles_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.debug_dir = self.output_dir / "debug"
        if debug_html:
            self.debug_dir.mkdir(parents=True, exist_ok=True)

        self.headless = headless
        self.debug_html = debug_html
        self.rate_limit = rate_limit

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self.logged_in = False

    async def start(self):
        """Initialize the browser and context."""
        logger.info("Starting browser...")
        self.playwright = await async_playwright().start()

        # Launch browser with anti-detection settings
        launch_args = {
            'headless': self.headless,
        }

        if self.headless:
            launch_args['args'] = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]

        self.browser = await self.playwright.chromium.launch(**launch_args)

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )

        # Mask automation signals
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        self.page = await self.context.new_page()
        logger.info("Browser started successfully")

    async def close(self):
        """Close the browser."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")

    async def login(self) -> bool:
        """
        Log into Crunchbase.

        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info(f"Navigating to login page: {self.LOGIN_URL}")
            await self.page.goto(self.LOGIN_URL, wait_until='networkidle', timeout=30000)

            # Wait for login form
            await self.page.wait_for_selector('input[type="email"], input[name="email"]', timeout=10000)

            logger.info("Filling in login credentials...")

            # Fill email
            email_selector = 'input[type="email"], input[name="email"]'
            await self.page.fill(email_selector, self.email)

            # Fill password
            password_selector = 'input[type="password"], input[name="password"]'
            await self.page.fill(password_selector, self.password)

            # Click login button
            login_button_selector = 'button[type="submit"], button:has-text("Log in"), button:has-text("Sign in")'
            await self.page.click(login_button_selector)

            logger.info("Waiting for login to complete...")

            # Wait for navigation after login
            await self.page.wait_for_load_state('networkidle', timeout=30000)

            # Check if login was successful by looking for common post-login elements
            # or checking if we're still on the login page
            current_url = self.page.url
            if 'login' not in current_url.lower():
                logger.info("Login successful!")
                self.logged_in = True
                return True
            else:
                logger.error("Login failed - still on login page")
                return False

        except Exception as e:
            logger.error(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def extract_profile_data(self, profile_name: str) -> Dict[str, Any]:
        """
        Extract data from a person profile page.

        Args:
            profile_name: The profile identifier (e.g., "elon-musk")

        Returns:
            Dictionary containing extracted profile data
        """
        profile_url = f"{self.BASE_URL}/person/{profile_name}"
        logger.info(f"Extracting data from: {profile_url}")

        try:
            await self.page.goto(profile_url, wait_until='networkidle', timeout=30000)

            # Wait for content to load
            await asyncio.sleep(3)  # Give time for dynamic content

            # Save debug HTML if enabled
            if self.debug_html:
                html_content = await self.page.content()
                debug_file = self.debug_dir / f"{profile_name}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Saved debug HTML to {debug_file}")

            # Extract data
            data = {
                'profile_name': profile_name,
                'url': profile_url,
                'scraped_at': datetime.utcnow().isoformat(),
            }

            # Extract full name
            try:
                name_elem = await self.page.query_selector('h1, [class*="profile-name"], [class*="person-name"]')
                if name_elem:
                    data['name'] = await name_elem.inner_text()
                    logger.info(f"Extracted name: {data['name']}")
            except Exception as e:
                logger.warning(f"Could not extract name: {e}")

            # Extract overview/bio
            try:
                overview_selectors = [
                    '[class*="overview"]',
                    '[class*="description"]',
                    '[class*="bio"]',
                    'section:has-text("Overview")',
                ]

                for selector in overview_selectors:
                    overview_elem = await self.page.query_selector(selector)
                    if overview_elem:
                        data['overview'] = await overview_elem.inner_text()
                        logger.info(f"Extracted overview ({len(data['overview'])} chars)")
                        break
            except Exception as e:
                logger.warning(f"Could not extract overview: {e}")

            # Extract links (social, website, etc.)
            try:
                links = []
                link_elements = await self.page.query_selector_all('a[href*="linkedin.com"], a[href*="twitter.com"], a[href*="facebook.com"], a[href*="instagram.com"], [class*="social"] a, [class*="link"] a')

                for elem in link_elements:
                    href = await elem.get_attribute('href')
                    if href and href.startswith('http'):
                        # Get link text/label if available
                        text = await elem.inner_text()
                        link_data = {'url': href}
                        if text.strip():
                            link_data['label'] = text.strip()

                        # Determine link type
                        if 'linkedin.com' in href:
                            link_data['type'] = 'linkedin'
                        elif 'twitter.com' in href or 'x.com' in href:
                            link_data['type'] = 'twitter'
                        elif 'facebook.com' in href:
                            link_data['type'] = 'facebook'
                        elif 'instagram.com' in href:
                            link_data['type'] = 'instagram'
                        else:
                            link_data['type'] = 'website'

                        if link_data not in links:
                            links.append(link_data)

                if links:
                    data['links'] = links
                    logger.info(f"Extracted {len(links)} links")
            except Exception as e:
                logger.warning(f"Could not extract links: {e}")

            # Extract jobs/work experience
            try:
                jobs = []

                # Look for job/work experience sections
                job_sections = await self.page.query_selector_all(
                    '[class*="job"], [class*="position"], [class*="experience"], [class*="employment"]'
                )

                for job_elem in job_sections:
                    try:
                        job_data = {}

                        # Try to extract job title
                        title_elem = await job_elem.query_selector('h3, h4, [class*="title"], [class*="position"]')
                        if title_elem:
                            job_data['title'] = await title_elem.inner_text()

                        # Try to extract company
                        company_elem = await job_elem.query_selector('[class*="company"], [class*="organization"]')
                        if company_elem:
                            job_data['company'] = await company_elem.inner_text()

                        # Try to extract dates
                        date_elem = await job_elem.query_selector('[class*="date"], [class*="duration"], time')
                        if date_elem:
                            job_data['dates'] = await date_elem.inner_text()

                        # Only add if we have meaningful data
                        if job_data.get('title') or job_data.get('company'):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error extracting job item: {e}")
                        continue

                if jobs:
                    data['jobs'] = jobs
                    logger.info(f"Extracted {len(jobs)} jobs")
                else:
                    # Alternative: try to get all text from jobs section
                    jobs_section = await self.page.query_selector('section:has-text("Job"), section:has-text("Experience"), section:has-text("Employment")')
                    if jobs_section:
                        data['jobs_text'] = await jobs_section.inner_text()
                        logger.info("Extracted jobs as text block")

            except Exception as e:
                logger.warning(f"Could not extract jobs: {e}")

            # Extract education
            try:
                education = []

                # Look for education sections
                edu_sections = await self.page.query_selector_all(
                    '[class*="education"], [class*="school"], [class*="university"]'
                )

                for edu_elem in edu_sections:
                    try:
                        edu_data = {}

                        # Try to extract school name
                        school_elem = await edu_elem.query_selector('h3, h4, [class*="school"], [class*="institution"]')
                        if school_elem:
                            edu_data['school'] = await school_elem.inner_text()

                        # Try to extract degree
                        degree_elem = await edu_elem.query_selector('[class*="degree"], [class*="program"]')
                        if degree_elem:
                            edu_data['degree'] = await degree_elem.inner_text()

                        # Try to extract dates
                        date_elem = await edu_elem.query_selector('[class*="date"], [class*="year"], time')
                        if date_elem:
                            edu_data['dates'] = await date_elem.inner_text()

                        # Only add if we have meaningful data
                        if edu_data.get('school') or edu_data.get('degree'):
                            education.append(edu_data)
                    except Exception as e:
                        logger.debug(f"Error extracting education item: {e}")
                        continue

                if education:
                    data['education'] = education
                    logger.info(f"Extracted {len(education)} education items")
                else:
                    # Alternative: try to get all text from education section
                    edu_section = await self.page.query_selector('section:has-text("Education")')
                    if edu_section:
                        data['education_text'] = await edu_section.inner_text()
                        logger.info("Extracted education as text block")

            except Exception as e:
                logger.warning(f"Could not extract education: {e}")

            logger.info(f"Successfully extracted data for {profile_name}")
            return data

        except Exception as e:
            logger.error(f"Error extracting profile {profile_name}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'profile_name': profile_name,
                'url': profile_url,
                'error': str(e),
                'scraped_at': datetime.utcnow().isoformat(),
            }

    def save_profile_json(self, profile_name: str, data: Dict[str, Any]) -> Path:
        """
        Save profile data to individual JSON file.

        Args:
            profile_name: Profile identifier
            data: Profile data to save

        Returns:
            Path to saved file
        """
        filename = f"{profile_name}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved profile data to {filepath}")
        return filepath

    def read_profiles(self) -> List[str]:
        """
        Read profile names from profiles.txt file.

        Returns:
            List of profile names
        """
        if not self.profiles_file.exists():
            logger.warning(f"Profiles file not found: {self.profiles_file}")
            return []

        profiles = []
        with open(self.profiles_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    profiles.append(line)

        logger.info(f"Read {len(profiles)} profiles from {self.profiles_file}")
        return profiles

    async def crawl(self):
        """
        Main crawl method - processes all profiles from profiles.txt.
        """
        # Read profiles from file
        profiles = self.read_profiles()

        if not profiles:
            logger.error("No profiles to process!")
            return

        logger.info(f"Starting to crawl {len(profiles)} profiles...")

        # Login first
        if not self.logged_in:
            login_success = await self.login()
            if not login_success:
                logger.error("Login failed - cannot continue")
                return

        # Process each profile
        successful = 0
        failed = 0

        for i, profile_name in enumerate(profiles, 1):
            logger.info(f"\n[{i}/{len(profiles)}] Processing profile: {profile_name}")

            try:
                # Extract profile data
                data = await self.extract_profile_data(profile_name)

                # Save to JSON
                self.save_profile_json(profile_name, data)

                if 'error' not in data:
                    successful += 1
                else:
                    failed += 1

                # Rate limiting
                if i < len(profiles):  # Don't wait after last profile
                    logger.info(f"Waiting {self.rate_limit}s before next profile...")
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                logger.error(f"Failed to process {profile_name}: {e}")
                failed += 1
                continue

        logger.info(f"\n{'='*60}")
        logger.info(f"Crawl complete!")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total: {len(profiles)}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"{'='*60}")


async def main():
    """Example usage of the crawler."""

    # Configuration
    EMAIL = "joy.i.mikhael@outlook.com"
    PASSWORD = "Bane70213365"
    PROFILES_FILE = "crawlers/crunchbase/profiles.txt"
    OUTPUT_DIR = "data/crunchbase/profiles"

    crawler = CrunchbaseProfileCrawler(
        email=EMAIL,
        password=PASSWORD,
        profiles_file=PROFILES_FILE,
        output_dir=OUTPUT_DIR,
        headless=True,  # Set to False to see browser
        debug_html=True,  # Save HTML for debugging
        rate_limit=2.0  # Wait 2 seconds between profiles
    )

    try:
        await crawler.start()
        await crawler.crawl()
    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
