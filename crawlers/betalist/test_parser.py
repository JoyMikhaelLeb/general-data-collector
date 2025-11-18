#!/usr/bin/env python3
"""
Test script to verify the betalist parser works with actual HTML structure.
"""
import sys
import json
from pathlib import Path

# Add parent directory to path to import crawler
sys.path.insert(0, str(Path(__file__).parent))

from crawler import BetalistCrawler

# Actual HTML from betalist.com with date headers
sample_html = """
<html>
<body>
<div class="col-span-full text-3xl text-gray-300 dark:text-gray-600 [&>strong]:text-black dark:[&>strong]:text-white -xmb-24" data-duplicate-id="day_1763424000">
  <strong>Today</strong> November 18th
</div>
<div class="block" id="startup-135459">
  <a class="block min-w-[128px] rounded-sm overflow-hidden relative aspect-4/3 ring-1 ring-black/5 dark:ring-white/10 hover:ring-black/10 dark:hover:ring-white/20 hover:after:block hover:after:absolute hover:after:inset-0 hover:after:bg-black/10 dark:hover:after:bg-white/10" style="background-color: #110f18" href="/startups/cliowright">
    <img srcset="https://resize.imagekit.co/_axL5msliB5FPWRZSZCn2uQ5MHAeRHXNDs02u1aHUY4/rs:fill:480:360/dpr:1/plain/s3://betalist-production/r3kim3bjds8yio4tn0suetrjv2l5 1x" class="block object-cover absolute inset-0 h-full w-full" src="https://resize.imagekit.co/wMcJKw61N4F_Zzk2Yq68wbSxuyblxuza-KnNV9fk7hY/rs:fill:480:360/plain/s3://betalist-production/r3kim3bjds8yio4tn0suetrjv2l5">
  </a>
  <div class="block">
    <div class="mt-3 text-base">
      <div class="flex items-start gap-2">
        <a class="block whitespace-nowrap text-ellipsis overflow-hidden font-medium text-gray-900 dark:text-gray-100" href="/startups/cliowright">ClioWright</a>
      </div>
      <a class="block text-gray-500 dark:text-gray-400" href="/startups/cliowright">AI writing assistant</a>
    </div>
  </div>
</div>

<div class="col-span-full text-3xl text-gray-300 dark:text-gray-600 [&>strong]:text-black dark:[&>strong]:text-white -xmb-24" data-duplicate-id="day_1763337600">
  <strong>Yesterday</strong> November 17th
</div>
<div class="block" id="startup-134804">
  <a class="block min-w-[128px] rounded-sm overflow-hidden relative aspect-4/3" style="background-color: #d5f5ea" href="/startups/nextjsshop">
    <img src="https://resize.imagekit.co/xmiq7XJ2UvU4kiSlhoYe_OvZTX1Ek_aEGAKYKdlI2Y8/rs:fill:480:360/plain/s3://betalist-production/ekrspv9n19q4r537z8cfcytj3ove">
  </a>
  <div class="block">
    <div class="mt-3 text-base">
      <div class="flex items-start gap-2">
        <a class="block whitespace-nowrap text-ellipsis overflow-hidden font-medium text-gray-900 dark:text-gray-100" href="/startups/nextjsshop">Nextjsshop</a>
      </div>
      <a class="block text-gray-500 dark:text-gray-400" href="/startups/nextjsshop">Marketplace for Nextjs</a>
    </div>
  </div>
</div>
</body>
</html>
"""

def main():
    """Test the parser with real HTML."""
    crawler = BetalistCrawler()

    # Test parse_page method
    items = crawler.parse_page(sample_html, "https://betalist.com/")

    print(f"\n{'='*60}")
    print(f"Parser Test Results")
    print(f"{'='*60}")
    print(f"Found {len(items)} items\n")

    if items:
        print("Extracted data:")
        print(json.dumps(items, indent=2))

        print(f"\n{'='*60}")
        print(f"✓ Parser working correctly!")
        print(f"{'='*60}")

        # Verify expected fields
        first_item = items[0]
        expected_fields = ['source', 'url', 'scraped_at', 'startup_id', 'title', 'description', 'link', 'logo', 'date_launched']

        print("\nField verification:")
        for field in expected_fields:
            status = "✓" if field in first_item else "✗"
            value = first_item.get(field, "MISSING")
            print(f"  {status} {field}: {value[:50] if isinstance(value, str) and len(value) > 50 else value}")

        # Verify dates are correctly assigned
        print("\nDate verification:")
        for i, item in enumerate(items):
            print(f"  Item {i+1}: {item.get('title')} -> date_launched: {item.get('date_launched', 'MISSING')}")
    else:
        print("✗ No items extracted - parser may need adjustment")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
