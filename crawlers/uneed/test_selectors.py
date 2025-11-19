#!/usr/bin/env python3
"""
Test script to debug HTML selectors for Uneed crawler.
Run this with network access to see what the crawler is actually finding.
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def test_selectors():
    """Test different selectors on the actual uneed.best page."""
    url = "https://www.uneed.best"

    print(f"Fetching {url}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"❌ HTTP {response.status}")
                    return

                html = await response.text()
                print(f"✓ Fetched HTML ({len(html)} bytes)")

                # Save for inspection
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✓ Saved to debug_page.html")

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                print("\n" + "="*60)
                print("TESTING SELECTORS")
                print("="*60)

                # Test 1: Look for the specific anchor class
                print("\n1. Testing: a.flex.relative.items-center.py-4.w-full.group")
                anchors = soup.find_all('a', class_='flex relative items-center py-4 w-full group')
                print(f"   Found: {len(anchors)} elements")
                if anchors:
                    for i, a in enumerate(anchors[:3], 1):
                        href = a.get('href', 'NO HREF')
                        print(f"   [{i}] {href}")

                # Test 2: Look for any links with /tool/
                print("\n2. Testing: Any <a> with href containing '/tool/'")
                tool_links = soup.find_all('a', href=lambda x: x and '/tool/' in x)
                print(f"   Found: {len(tool_links)} elements")
                if tool_links:
                    for i, link in enumerate(tool_links[:5], 1):
                        href = link.get('href')
                        classes = ' '.join(link.get('class', []))
                        print(f"   [{i}] {href}")
                        print(f"       Classes: {classes[:80]}")

                # Test 3: Look for divs with 'flex flex-col'
                print("\n3. Testing: div.flex.flex-col")
                divs = soup.find_all('div', class_='flex flex-col')
                print(f"   Found: {len(divs)} elements")
                if divs:
                    for i, div in enumerate(divs[:3], 1):
                        child_divs = div.find_all('div', class_='relative', recursive=False)
                        print(f"   [{i}] Has {len(child_divs)} child divs with class 'relative'")

                # Test 4: Look for divs with 'pb-4 w-full'
                print("\n4. Testing: div.pb-4.w-full")
                divs = soup.find_all('div', class_='pb-4 w-full')
                print(f"   Found: {len(divs)} elements")

                # Test 5: Count all divs with class 'relative'
                print("\n5. Testing: div.relative")
                relative_divs = soup.find_all('div', class_='relative')
                print(f"   Found: {len(relative_divs)} elements")

                # Test 6: Show structure of first few links
                print("\n6. Structure Analysis: First 3 links on page")
                all_links = soup.find_all('a', href=True)[:3]
                for i, link in enumerate(all_links, 1):
                    href = link.get('href', '')
                    classes = link.get('class', [])
                    parent = link.parent.name if link.parent else 'None'
                    parent_class = ' '.join(link.parent.get('class', [])) if link.parent and link.parent.get('class') else 'None'

                    print(f"\n   Link {i}:")
                    print(f"   href: {href}")
                    print(f"   classes: {' '.join(classes)}")
                    print(f"   parent: <{parent} class='{parent_class}'>")

                print("\n" + "="*60)
                print("✓ Test complete. Check debug_page.html for full HTML")
                print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_selectors())
