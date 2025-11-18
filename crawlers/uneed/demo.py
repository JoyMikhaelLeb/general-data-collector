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
        "tool_name": "AI Design Assistant",
        "tool_link": "https://www.uneed.best/tool/example-tool-1",
        "tool_info": {
            "overview": "Revolutionary AI-powered design tool that helps you create stunning visuals in minutes",
            "publisher_name": "John Smith",
            "publisher_link": "https://www.uneed.best/user/johnsmith",
            "general_info": {
                "launch_date": "2025-11-18",
                "categories": ["Design Tools", "AI"],
                "pricing": "Free with premium options",
                "website": "https://example-tool.com",
                "socials": {
                    "twitter": "https://twitter.com/exampletool",
                    "linkedin": "https://linkedin.com/company/exampletool"
                },
                "for_sale": False
            }
        }
    },
    {
        "tool_name": "ProductivityMax",
        "tool_link": "https://www.uneed.best/tool/example-tool-2",
        "tool_info": {
            "overview": "All-in-one productivity suite for remote teams",
            "publisher_name": "Sarah Johnson",
            "publisher_link": "https://www.uneed.best/user/sarahj",
            "general_info": {
                "launch_date": "2025-11-17",
                "categories": ["Productivity"],
                "pricing": "$29/month",
                "website": "https://productivitymax.io",
                "socials": {
                    "twitter": "https://twitter.com/productivitymax",
                    "github": "https://github.com/productivitymax"
                }
            }
        }
    },
    {
        "tool_name": "CodeHelper AI",
        "tool_link": "https://www.uneed.best/tool/example-tool-3",
        "tool_info": {
            "overview": "AI coding assistant that writes clean, production-ready code",
            "publisher_name": "DevTeam Inc",
            "publisher_link": "https://www.uneed.best/user/devteam",
            "general_info": {
                "launch_date": "2025-11-16",
                "categories": ["Developer Tools"],
                "pricing": "Free",
                "website": "https://codehelper.dev",
                "for_sale": True
            }
        }
    }
]

def main():
    """Create demo JSON output."""
    output_dir = Path("data/uneed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use the new date format: uneed-DDMMYYYY.json
    date_str = datetime.now().strftime("%d%m%Y")
    filename = f"uneed-{date_str}-demo.json"
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
