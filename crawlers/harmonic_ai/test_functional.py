#!/usr/bin/env python3
"""
Simple test to verify crawler functionality without network access.
"""

import asyncio
from crawler import HarmonicCrawler


async def test_crawler_initialization():
    """Test that crawler initializes correctly."""
    print("Testing crawler initialization...")

    crawler = HarmonicCrawler(output_dir="test_data", rate_limit=0.5)

    # Check initialization
    assert crawler.output_dir.name == "test_data"
    assert crawler.rate_limit == 0.5
    assert crawler.max_retries == 3
    assert crawler.data == []

    print("✓ Initialization test passed")


async def test_session_lifecycle():
    """Test session start and close."""
    print("\nTesting session lifecycle...")

    async with HarmonicCrawler() as crawler:
        assert crawler.session is not None
        print("✓ Session started")

    print("✓ Session closed")
    print("✓ Context manager test passed")


async def test_parsing():
    """Test HTML parsing without network."""
    print("\nTesting HTML parsing...")

    crawler = HarmonicCrawler()

    # Sample HTML
    html = """
    <html>
        <body>
            <div class="company">
                <h2 class="title">Test Startup Inc.</h2>
                <p class="description">An innovative AI-powered platform</p>
                <a href="/company/test-startup">View Details</a>
            </div>
            <div class="company">
                <h2 class="title">Data Corp</h2>
                <p class="description">Enterprise data solutions</p>
                <a href="/company/data-corp">Learn More</a>
            </div>
        </body>
    </html>
    """

    items = crawler.parse_page(html, "https://harmonic.ai/companies")

    assert len(items) == 2
    assert items[0]['title'] == "Test Startup Inc."
    assert items[0]['description'] == "An innovative AI-powered platform"
    assert items[0]['source'] == "harmonic.ai"
    assert items[1]['title'] == "Data Corp"

    print(f"✓ Parsed {len(items)} items successfully")
    print(f"  - Item 1: {items[0]['title']}")
    print(f"  - Item 2: {items[1]['title']}")
    print("✓ Parsing test passed")


async def test_data_export():
    """Test JSON and CSV export."""
    print("\nTesting data export...")

    crawler = HarmonicCrawler(output_dir="test_data")

    # Add sample data
    crawler.data = [
        {
            'source': 'harmonic.ai',
            'url': 'https://harmonic.ai/test',
            'scraped_at': '2025-11-16T12:00:00',
            'title': 'Test Company',
            'description': 'A test company',
            'link': 'https://harmonic.ai/company/test'
        }
    ]

    # Test JSON export
    json_path = crawler.save_json("test_output.json")
    assert json_path.exists()
    print(f"✓ JSON exported to: {json_path}")

    # Test CSV export
    csv_path = crawler.save_csv("test_output.csv")
    assert csv_path.exists()
    print(f"✓ CSV exported to: {csv_path}")

    print("✓ Export test passed")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Harmonic AI Crawler - Functional Tests")
    print("=" * 60)

    try:
        await test_crawler_initialization()
        await test_session_lifecycle()
        await test_parsing()
        await test_data_export()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe crawler is working correctly!")
        print("- Initialization: ✓")
        print("- Session management: ✓")
        print("- HTML parsing: ✓")
        print("- Data export (JSON/CSV): ✓")
        print("\nNote: Network tests skipped (no internet access)")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
