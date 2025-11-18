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
        "title": "ClioWright",
        "description": "AI writing assistant",
        "link": "https://betalist.com/startups/cliowright",
        "logo": "https://resize.imagekit.co/wMcJKw61N4F_Zzk2Yq68wbSxuyblxuza-KnNV9fk7hY/rs:fill:480:360/plain/s3://betalist-production/r3kim3bjds8yio4tn0suetrjv2l5",
        "date_launched": "18-11-2025"
    },
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "startup_id": "134804",
        "title": "Nextjsshop",
        "description": "Marketplace for Nextjs",
        "link": "https://betalist.com/startups/nextjsshop",
        "logo": "https://resize.imagekit.co/xmiq7XJ2UvU4kiSlhoYe_OvZTX1Ek_aEGAKYKdlI2Y8/rs:fill:480:360/plain/s3://betalist-production/ekrspv9n19q4r537z8cfcytj3ove",
        "date_launched": "17-11-2025"
    },
    {
        "source": "betalist",
        "url": "https://betalist.com/",
        "scraped_at": datetime.utcnow().isoformat(),
        "startup_id": "134803",
        "title": "Skilltracker",
        "description": "Track your skills and progress",
        "link": "https://betalist.com/startups/skilltracker",
        "date_launched": "16-11-2025"
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
