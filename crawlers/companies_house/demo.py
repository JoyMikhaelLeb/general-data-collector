#!/usr/bin/env python3
"""
Demo script showing the expected JSON output format for Companies House crawler.
This demonstrates what the crawler will produce when it has network access.
"""
import json
from datetime import datetime
from pathlib import Path

# Sample data showing expected structure with detailed company information
sample_data = [
    {
        "source": "companies_house_uk",
        "search_query": "HSBC Holdings",
        "scraped_at": datetime.utcnow().isoformat(),
        "company_link": "https://find-and-update.company-information.service.gov.uk/company/00617987",
        "company_number": "00617987",
        "company_name": "HSBC HOLDINGS PLC",
        "company_status": "Active",
        "company_type": "Public limited company",
        "incorporation_date": "27 July 1990",
        "registered_address": "8 Canada Square, London, E14 5HQ",
        "nature_of_business": "64191 - Banks",
        "accounts_info": "Next accounts made up to 31 December 2025 due by 30 September 2026",
        "confirmation_statement": "Next statement date 31 December 2025 due by 14 January 2026"
    },
    {
        "source": "companies_house_uk",
        "search_query": "Tesco",
        "scraped_at": datetime.utcnow().isoformat(),
        "company_link": "https://find-and-update.company-information.service.gov.uk/company/00445790",
        "company_number": "00445790",
        "company_name": "TESCO PLC",
        "company_status": "Active",
        "company_type": "Public limited company",
        "incorporation_date": "27 November 1932",
        "registered_address": "Tesco House, Shire Park, Kestrel Way, Welwyn Garden City, AL7 1GA",
        "nature_of_business": "47110 - Retail sale in non-specialised stores with food, beverages or tobacco predominating",
        "accounts_info": "Next accounts made up to 28 February 2026 due by 30 November 2026",
        "confirmation_statement": "Next statement date 28 February 2026 due by 14 March 2026"
    },
    {
        "source": "companies_house_uk",
        "search_query": "Vodafone",
        "scraped_at": datetime.utcnow().isoformat(),
        "company_link": "https://find-and-update.company-information.service.gov.uk/company/01833679",
        "company_number": "01833679",
        "company_name": "VODAFONE GROUP PUBLIC LIMITED COMPANY",
        "company_status": "Active",
        "company_type": "Public limited company",
        "incorporation_date": "30 August 1984",
        "registered_address": "Vodafone House, The Connection, Newbury, Berkshire, RG14 2FN",
        "nature_of_business": "61900 - Other telecommunications activities",
        "accounts_info": "Next accounts made up to 31 March 2026 due by 30 December 2026",
        "confirmation_statement": "Next statement date 31 March 2026 due by 14 April 2026"
    }
]

def main():
    """Create demo JSON output."""
    output_dir = Path("data/companies_house")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"companies_demo_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Demo JSON created: {filepath}")
    print(f"{'='*60}")
    print(f"\nThis demonstrates the expected output format.")
    print(f"When the crawler runs with network access, it will produce")
    print(f"JSON files with this structure containing real company data.\n")
    print("Sample output:")
    print(json.dumps(sample_data[0], indent=2))
    print(f"\n{'='*60}")
    print(f"Total items: {len(sample_data)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
