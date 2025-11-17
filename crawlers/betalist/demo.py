#!/usr/bin/env python3
"""
Demo script showing the expected JSON output format for betalist crawler.
This demonstrates what the crawler will produce when it has network access.
"""
import json
from datetime import datetime
from pathlib import Path

# Sample data showing expected structure
sample_data = [
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "startup_id": "135459",
        "title": "SubWatch",
        "description": "Never forget a subscription payment again",
        "link": "https://betalist.com/startups/subwatch-2",
        "logo": "https://resize.imagekit.co/wMcJKw61N4F_Zzk2Yq68wbSxuyblxuza-KnNV9fk7hY/rs:fill:480:360/plain/s3://betalist-production/r3kim3bjds8yio4tn0suetrjv2l5"
    },
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "startup_id": "135460",
        "title": "Example Startup 2",
        "description": "Next-gen productivity app for remote teams",
        "link": "https://betalist.com/startups/example-2",
        "logo": "https://betalist.com/images/example2.jpg"
    },
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "startup_id": "135461",
        "title": "Example Startup 3",
        "description": "Social platform connecting creators worldwide",
        "link": "https://betalist.com/startups/example-3"
    }
]

def main():
    """Create demo JSON output."""
    output_dir = Path("data/betalist")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"betalist_demo_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Demo JSON created: {filepath}")
    print(f"{'='*60}")
    print(f"\nThis demonstrates the expected output format.")
    print(f"When the crawler runs with network access, it will produce")
    print(f"JSON files with this structure containing real startup data.\n")
    print("Sample output:")
    print(json.dumps(sample_data[0], indent=2))
    print(f"\n{'='*60}")
    print(f"Total items: {len(sample_data)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
