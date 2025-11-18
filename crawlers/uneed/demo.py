#!/usr/bin/env python3
"""
Demo script showing the expected JSON output format for Uneed crawler.
This demonstrates what the crawler will produce when it has network access.
"""
import json
from datetime import datetime
from pathlib import Path

# Sample data showing expected structure
sample_data = [
    {
        "source": "uneed_best",
        "scraped_at": datetime.utcnow().isoformat(),
        "tool_url": "https://www.uneed.best/tool/example-tool-1",
        "tool_name": "AI Design Assistant",
        "overview": "Revolutionary AI-powered design tool that helps you create stunning visuals in minutes",
        "website": "https://example-tool.com",
        "publisher_name": "John Smith",
        "publisher_link": "https://www.uneed.best/user/johnsmith",
        "launch_date": "2025-11-18",
        "category": "Design Tools",
        "pricing": "Free with premium options",
        "socials": {
            "twitter": "https://twitter.com/exampletool",
            "linkedin": "https://linkedin.com/company/exampletool"
        },
        "for_sale": False
    },
    {
        "source": "uneed_best",
        "scraped_at": datetime.utcnow().isoformat(),
        "tool_url": "https://www.uneed.best/tool/example-tool-2",
        "tool_name": "ProductivityMax",
        "overview": "All-in-one productivity suite for remote teams",
        "website": "https://productivitymax.io",
        "publisher_name": "Sarah Johnson",
        "publisher_link": "https://www.uneed.best/user/sarahj",
        "launch_date": "2025-11-17",
        "category": "Productivity",
        "pricing": "$29/month",
        "socials": {
            "twitter": "https://twitter.com/productivitymax",
            "github": "https://github.com/productivitymax"
        }
    },
    {
        "source": "uneed_best",
        "scraped_at": datetime.utcnow().isoformat(),
        "tool_url": "https://www.uneed.best/tool/example-tool-3",
        "tool_name": "CodeHelper AI",
        "overview": "AI coding assistant that writes clean, production-ready code",
        "website": "https://codehelper.dev",
        "publisher_name": "DevTeam Inc",
        "launch_date": "2025-11-16",
        "category": "Developer Tools",
        "pricing": "Free",
        "for_sale": True
    }
]

def main():
    """Create demo JSON output."""
    output_dir = Path("data/uneed")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"uneed_demo_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Demo JSON created: {filepath}")
    print(f"{'='*60}")
    print(f"\nThis demonstrates the expected output format.")
    print(f"When the crawler runs with network access, it will produce")
    print(f"JSON files with this structure containing real tool data.\n")
    print("Sample output:")
    print(json.dumps(sample_data[0], indent=2))
    print(f"\n{'='*60}")
    print(f"Total items: {len(sample_data)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
