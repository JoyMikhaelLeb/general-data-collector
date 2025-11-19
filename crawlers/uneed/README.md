# Uneed.best Crawler

## The Problem: JavaScript-Rendered Content

The uneed.best website is a **Single Page Application (SPA)** that loads tool listings dynamically with JavaScript. When we fetch the HTML directly (like `crawler.py` does), we only get the initial page shell without the actual tool content.

**Evidence:**
- Direct HTML fetch finds only 48 anchors (navigation links)
- No `/tool/` links in the initial HTML
- Tool content loads after page renders

## Solution: Browser-Based Crawler

Use `crawler_browser.py` which launches a real browser to render JavaScript.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (one-time setup)
playwright install chromium
```

## Usage

### Browser Crawler (Recommended)

**With visible browser** (good for debugging):
```bash
python3 crawler_browser.py
```

This opens a visible Chrome browser window so you can see what's happening.

**Headless mode** (faster, no window):
Edit `crawler_browser.py` and change:
```python
async with UneedBrowserCrawler(headless=True, debug_html=True) as crawler:
```

### Regular Crawler (Won't Work for This Site)

```bash
python3 crawler.py
```

This only works for server-rendered HTML sites. For uneed.best, it returns 0 results because the content is JavaScript-loaded.

## How It Works

### Browser Crawler

1. Launches a real Chrome browser (using Playwright)
2. Navigates to https://www.uneed.best
3. Waits for JavaScript to render the page
4. Waits specifically for tool links: `a[href*="/tool/"]`
5. Extracts the fully-rendered HTML
6. Parses tool links
7. Visits each tool page and extracts details

### What Gets Extracted

- `tool_name`: Name of the tool
- `overview`: Description
- `tool_url`: Link to tool page on uneed.best
- `website`: Official tool website
- `category`: Tool category/tags
- `pricing`: Pricing information
- `socials`: Social media links
- `launch_date`: When it was launched

## Output Files

- `data/uneed/uneed_TIMESTAMP.json` - Crawled data
- `data/uneed/crawler_browser.log` - Detailed logs
- `data/uneed/debug/main_page_rendered.html` - Saved rendered HTML

## Troubleshooting

### "No tool links found in rendered HTML"

The wait selector might not be working. Try increasing the wait time:

```python
# In crawler_browser.py, change:
await page.wait_for_timeout(2000)  # Increase to 5000
```

### Browser won't start

Make sure Playwright browsers are installed:
```bash
playwright install chromium
```

### Want to see what's happening?

Run with `headless=False`:
```python
async with UneedBrowserCrawler(headless=False, debug_html=True) as crawler:
```

This opens a visible browser window.

## Comparison: crawler.py vs crawler_browser.py

| Feature | crawler.py | crawler_browser.py |
|---------|-----------|-------------------|
| **Speed** | Fast (HTTP only) | Slower (renders JS) |
| **Works for uneed.best** | ❌ No (0 results) | ✅ Yes |
| **Dependencies** | aiohttp, bs4 | +playwright |
| **Browser required** | No | Yes (Chromium) |
| **Use case** | Server-rendered HTML | JavaScript SPAs |

## Why the Regular Crawler Failed

When you run `crawler.py` and look at the debug output:

```
Total anchors on page: 48
Sample of first 10 anchors:
  [1] href=/
  [2] href=/
  [3] href=/community
  [4] href=/pricing
  ...
```

These are just navigation links! The tool listings aren't in the HTML because they load via JavaScript after the page renders.

The browser crawler solves this by:
1. Loading the page in a real browser
2. Waiting for JavaScript to execute
3. Waiting for tool links to appear
4. Then extracting the rendered content

## Performance Tips

- Use `headless=True` for production (faster)
- Adjust `rate_limit` to be respectful (default: 2 seconds)
- The first page load is slow (JS rendering), subsequent pages are faster

## Example Output

```json
[
  {
    "source": "uneed_best",
    "scraped_at": "2025-11-19T12:00:00.000000",
    "tool_url": "https://www.uneed.best/tool/email-checker",
    "tool_name": "Email Checker",
    "overview": "Fast, Accurate Bulk List Email Checker & API You Can Trust"
  }
]
```
