---
name: web-browser
description: "Use this skill when you need to interact with web pages that require JavaScript rendering, fill forms, take screenshots, or extract content from single-page applications (SPAs). For simple static pages, use the WebFetch tool instead. This skill provides full browser automation via Playwright."
license: MIT
---

# Web Browser Skill

Full browser automation via Playwright + Chromium. Provides headless browsing capabilities for pages that require JavaScript execution, dynamic content rendering, or interactive automation.

## When to Use Browser vs WebFetch

| Scenario | Tool |
|---|---|
| Static HTML page, public API docs | WebFetch |
| SPA (React, Vue, Angular) | **web-browser** |
| JS-rendered content (dashboards, charts) | **web-browser** |
| Fill and submit forms | **web-browser** |
| Take screenshots of pages or elements | **web-browser** |
| Extract content behind client-side routing | **web-browser** |
| Simple GET request for HTML/JSON | WebFetch |

**Rule of thumb**: if the page works with `curl`, use WebFetch. If it needs a real browser, use this skill.

## Core Operations

### Navigate to a URL

Open a page and wait for it to fully load (including network requests):

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com", wait_until="networkidle")
    print(page.title())
    browser.close()
```

### Take a Screenshot

Capture the full page or a specific element:

```python
# Full page screenshot
page.screenshot(path="full_page.png", full_page=True)

# Element screenshot
element = page.query_selector("#main-content")
element.screenshot(path="element.png")

# Custom viewport screenshot
page = browser.new_page(viewport={"width": 1920, "height": 1080})
page.goto(url, wait_until="networkidle")
page.screenshot(path="desktop_view.png")
```

### Extract Text Content

Get visible text from the page, stripping scripts and styles:

```python
# All visible text
text = page.inner_text("body")

# Text from a specific section
content = page.inner_text("article")
# or
content = page.inner_text("#main-content")
```

### Fill Forms and Click Elements

Interact with page elements:

```python
# Fill input fields
page.fill("#username", "user@example.com")
page.fill("#password", "secret")

# Click a button
page.click("button[type='submit']")

# Select from dropdown
page.select_option("select#country", value="US")

# Check a checkbox
page.check("#agree-terms")
```

### Wait for Selectors

Wait for dynamic content to appear:

```python
# Wait for an element to be visible
page.wait_for_selector(".results-loaded", timeout=10000)

# Wait for navigation after click
with page.expect_navigation():
    page.click("a.next-page")

# Wait for a specific network response
with page.expect_response("**/api/data"):
    page.click("#load-data")
```

## Scripts Reference

### browse.py

Navigate to a URL, optionally take a screenshot, return page metadata as JSON.

```bash
python3 scripts/browse.py https://example.com
python3 scripts/browse.py https://example.com --screenshot page.png
python3 scripts/browse.py https://example.com --wait domcontentloaded --timeout 15000
python3 scripts/browse.py https://example.com --viewport-width 1920 --viewport-height 1080
```

**Output** (JSON):
```json
{
  "title": "Example Domain",
  "url": "https://example.com/",
  "html_length": 1256
}
```

### screenshot.py

Capture screenshots with fine-grained control: full page, element-based crop, or custom viewport.

```bash
python3 scripts/screenshot.py https://example.com -o screenshot.png
python3 scripts/screenshot.py https://example.com -o element.png --selector "#main-content"
python3 scripts/screenshot.py https://example.com -o mobile.png --viewport-width 375 --viewport-height 812
python3 scripts/screenshot.py https://example.com -o page.png --full-page
```

### extract_content.py

Extract page content and convert it to clean markdown. Automatically strips navigation, footer, ads, and other non-content elements.

```bash
python3 scripts/extract_content.py https://example.com
python3 scripts/extract_content.py https://example.com --selector "article"
python3 scripts/extract_content.py https://example.com -o content.md
python3 scripts/extract_content.py https://example.com --wait networkidle --timeout 20000
```
