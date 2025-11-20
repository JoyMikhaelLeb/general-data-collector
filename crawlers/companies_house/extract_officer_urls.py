#!/usr/bin/env python3
"""
Extract officer URLs from companies JSON output.

This helper script extracts all officer profile URLs from the output
of crawler_companies.py and saves them to officer_urls.txt for use
with crawler_profiles.py.

Usage:
    python3 extract_officer_urls.py data/companies_house/companies_20251120_120000.json
"""

import json
import sys
from pathlib import Path
from typing import Set


def extract_officer_urls(json_file: Path) -> Set[str]:
    """
    Extract unique officer URLs from companies JSON file.

    Args:
        json_file: Path to companies JSON file

    Returns:
        Set of unique officer URLs
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    officer_urls = set()

    for company in companies:
        officers = company.get('officers', [])
        for officer in officers:
            officer_link = officer.get('officer_link')
            if officer_link:
                officer_urls.add(officer_link)

    return officer_urls


def main():
    """Main function."""
    if len(sys.argv) < 2:
        # Find most recent companies JSON file
        data_dir = Path("data/companies_house")
        if not data_dir.exists():
            print("Error: data/companies_house directory not found")
            print("Run crawler_companies.py first")
            sys.exit(1)

        json_files = sorted(data_dir.glob("companies_*.json"), reverse=True)
        if not json_files:
            print("Error: No companies JSON files found")
            print("Run crawler_companies.py first")
            sys.exit(1)

        json_file = json_files[0]
        print(f"Using most recent file: {json_file}")
    else:
        json_file = Path(sys.argv[1])
        if not json_file.exists():
            print(f"Error: File not found: {json_file}")
            sys.exit(1)

    print(f"Extracting officer URLs from: {json_file}")
    officer_urls = extract_officer_urls(json_file)

    if not officer_urls:
        print("No officer URLs found in JSON file")
        print("Make sure the companies JSON includes officer data")
        sys.exit(1)

    # Save to officer_urls.txt
    output_file = Path("officer_urls.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in sorted(officer_urls):
            f.write(url + '\n')

    print(f"\n✓ Extracted {len(officer_urls)} unique officer URLs")
    print(f"✓ Saved to: {output_file}")
    print(f"\nNow run: python3 crawler_profiles.py")


if __name__ == "__main__":
    main()
