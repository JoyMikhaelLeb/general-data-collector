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
        "title": "Example Startup 1",
        "description": "A revolutionary AI-powered tool for developers",
        "link": "https://betalist.com/startups/example1",
        "category": "Developer Tools",
        "date": "2025-11-15",
        "logo": "https://betalist.com/logos/example1.png"
    },
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "title": "Example Startup 2",
        "description": "Next-gen productivity app for remote teams",
        "link": "https://betalist.com/startups/example2",
        "category": "Productivity",
        "date": "2025-11-14"
    },
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "title": "Example Startup 3",
        "description": "Social platform connecting creators worldwide",
        "link": "https://betalist.com/startups/example3",
        "category": "Social Media"
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
