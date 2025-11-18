# Uneed Crawler Troubleshooting Guide

## Common Issues and Solutions

### Problem: Crawler returns 0 results

This usually happens when the HTML selectors don't match the actual website structure. Here's how to diagnose and fix:

#### Step 1: Enable Debug Mode
The crawler now has enhanced debugging features. When you run it, it will:
- Save raw HTML files to `data/uneed/debug/`
- Create detailed logs in `data/uneed/crawler.log`
- Show which fields were extracted for each tool

#### Step 2: Check the Logs
After running the crawler, check `data/uneed/crawler.log` for:
- **"Total links found on page"** - Shows how many links were found
- **"Found tool link"** - Shows which tool links were identified
- **"Sample link"** warnings - If no tools were found, this shows what links ARE on the page

#### Step 3: Inspect the HTML
Check the saved HTML files in `data/uneed/debug/`:
- `main_page.html` - The homepage HTML
- `tool_*.html` - Individual tool page HTML (first 3 tools)

Use these to identify the actual HTML structure and update selectors if needed.

### How to Update Selectors

#### For Main Page (finding tool links)
Location: `crawler.py` line ~159

Current selectors look for:
- Links containing `/tool/`
- Links starting with `/t/`

If the website uses different URL patterns, update this section:
```python
if '/tool/' in href or href.startswith('/t/'):
```

#### For Tool Pages (extracting data)
Location: `crawler.py` lines ~199-407

The crawler tries multiple selectors for each field. Add new selectors based on what you find in the HTML:

**Tool Name** (line ~200):
```python
name_selectors = [
    'h1',
    '[class*="tool"] h1',
    # Add new selectors here
]
```

**Description** (line ~220):
```python
description_selectors = [
    '[class*="description"]',
    'meta[name="description"]',
    # Add new selectors here
]
```

## Recent Improvements

### Enhanced HTML Parsing
- Added multiple fallback selectors for each field
- Better detection of tool names, descriptions, categories, and pricing
- Improved social media link extraction
- Added metadata extraction from `<meta>` tags

### Better Debugging
- **debug_html=True**: Saves raw HTML files for inspection
- **Enhanced logging**: Shows exactly which fields were found
- **Warning messages**: Alerts when minimal data is extracted
- **Sample link logging**: Shows what links exist when no tools are found

### Improved URL Handling
- Removes URL fragments and query parameters to avoid duplicates
- Better detection of external vs internal links
- Filters out social media links when looking for website URLs

## Testing the Crawler

### With Network Access
```bash
cd crawlers/uneed
python3 crawler.py
```

### Interpreting Results
The crawler will output:
```
Total links found on page: 150
Found 24 unique tool links
Processing tool 1/24: https://www.uneed.best/tool/example
Extracted 7 fields for tool: Example Tool - Fields: tool_name, overview, website, category, pricing, socials
```

**Good signs:**
- Many links found (100+)
- Multiple tool links identified (10+)
- 5+ fields extracted per tool

**Bad signs:**
- "No tool links found" warning
- "Very little data extracted" warnings
- Fields extracted < 2

### Next Steps After 0 Results

1. **Check logs** - Look for error messages or warnings
2. **Inspect HTML** - Open debug HTML files and search for tool information
3. **Update selectors** - Based on actual HTML structure
4. **Test incrementally** - Run crawler and check logs after each change
5. **Report back** - Share the log file and HTML structure if still stuck

## Debug Output Files

All debug files are saved to `data/uneed/`:
- `crawler.log` - Detailed execution log with DEBUG level messages
- `debug/main_page.html` - Homepage HTML for analysis
- `debug/tool_*.html` - Sample tool pages (first 3)
- `uneed_TIMESTAMP.json` - Extracted data (if any)

## HTML Structure Examples

When inspecting HTML, look for patterns like:

### Tool Links
```html
<a href="/tool/example-tool">Example Tool</a>
<a href="/t/another-tool">Another Tool</a>
```

### Tool Information
```html
<h1>Tool Name</h1>
<div class="description">Tool description here</div>
<a class="website" href="https://example.com">Visit Website</a>
<span class="category">Productivity</span>
<div class="pricing">$29/month</div>
```

Use Chrome/Firefox DevTools on the actual website to find the correct selectors!
