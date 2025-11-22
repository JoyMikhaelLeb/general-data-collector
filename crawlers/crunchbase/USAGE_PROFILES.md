# Crunchbase Profile Crawler Usage Guide

## Overview

The `crunchbase_profile.py` script extracts detailed information from Crunchbase person profiles, including:
- Personal overview/bio
- Social media and website links
- Work experience/jobs
- Education history

Each profile is saved as an individual JSON file named `{profile}.json`.

## Setup

1. **Add profiles to extract:**
   Edit `profiles.txt` and add profile names (one per line):
   ```
   elon-musk
   sam-altman
   mark-zuckerberg
   ```

   The profile name is the URL slug from `https://www.crunchbase.com/person/{PROFILE-NAME}`

2. **Configure credentials:**
   The script uses the credentials configured in the main function:
   - Email: `joy.i.mikhael@outlook.com`
   - Password: `Bane70213365`

## Running the Crawler

### Basic usage:
```bash
cd /home/user/general-data-collector
python3 crawlers/crunchbase/crunchbase_profile.py
```

### With visible browser (for debugging):
Edit the script and change `headless=False` in the main function.

## Output

- **JSON files:** `data/crunchbase/profiles/{profile}.json`
- **Debug HTML:** `data/crunchbase/profiles/debug/{profile}.html` (if debug_html=True)

## Output Format

Each JSON file contains:
```json
{
  "profile_name": "elon-musk",
  "url": "https://www.crunchbase.com/person/elon-musk",
  "scraped_at": "2025-11-22T10:30:00.000000",
  "name": "Elon Musk",
  "overview": "Biography/overview text...",
  "links": [
    {
      "url": "https://twitter.com/elonmusk",
      "type": "twitter"
    },
    {
      "url": "https://linkedin.com/in/elonmusk",
      "type": "linkedin"
    }
  ],
  "jobs": [
    {
      "title": "CEO",
      "company": "Tesla",
      "dates": "2008 - Present"
    }
  ],
  "education": [
    {
      "school": "University of Pennsylvania",
      "degree": "Bachelor's in Physics",
      "dates": "1992 - 1997"
    }
  ]
}
```

## Features

- **Authenticated access:** Logs into Crunchbase using provided credentials
- **Anti-detection:** Uses Playwright with stealth settings to avoid bot detection
- **Rate limiting:** Configurable delay between profiles (default: 2 seconds)
- **Debug mode:** Save HTML files to inspect page structure
- **Error handling:** Continues processing even if individual profiles fail
- **Individual JSON files:** Each profile saved separately for easy access

## Configuration Options

Edit the `main()` function in the script to customize:

- `headless`: Run browser in headless mode (default: True)
- `debug_html`: Save HTML files for debugging (default: True)
- `rate_limit`: Seconds between profile requests (default: 2.0)
- `output_dir`: Where to save JSON files (default: data/crunchbase/profiles)

## Troubleshooting

1. **Login fails:**
   - Check credentials are correct
   - Run with `headless=False` to see what's happening
   - Crunchbase may require CAPTCHA or 2FA

2. **No data extracted:**
   - Check debug HTML files in `data/crunchbase/profiles/debug/`
   - Crunchbase may have changed their page structure
   - Update selectors in the script based on actual HTML

3. **Profile not found:**
   - Verify the profile name is correct (check the URL on Crunchbase)
   - Some profiles may be private or restricted

## Examples

### Extract specific profiles:
```bash
# Edit profiles.txt:
echo "elon-musk" > crawlers/crunchbase/profiles.txt
echo "sam-altman" >> crawlers/crunchbase/profiles.txt

# Run crawler:
python3 crawlers/crunchbase/crunchbase_profile.py
```

### Check results:
```bash
# List extracted profiles:
ls -lh data/crunchbase/profiles/*.json

# View a profile:
cat data/crunchbase/profiles/elon-musk.json | jq
```
