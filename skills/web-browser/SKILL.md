---
name: web-browser
description: "Use this skill when you need to interact with web pages that require JavaScript rendering, fill forms, take screenshots, or extract content from single-page applications (SPAs). Provides full browser automation via Playwright + Chromium. For simple static pages, use a plain HTTP fetch instead."
license: MIT
---

# Web Browser

## Requirements

- **System:** `python3`, Playwright Chromium (`playwright install chromium`)
- **Python:** see `requirements.txt`

Full browser automation via Playwright + Chromium. Provides headless browsing capabilities for pages that require JavaScript execution, dynamic content rendering, or interactive automation.

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
# First install: ~525 MB disk, ~1-2 min download
#   (Chromium ~330 MB + headless_shell ~190 MB)
```

**Runtime resource notes:**
- Peak RAM ~400 MB per browser session. On constrained environments (<=2 GB), run only one session at a time.
- Browsers land in `~/Library/Caches/ms-playwright` (macOS) or `~/.cache/ms-playwright` (Linux) unless `PLAYWRIGHT_BROWSERS_PATH` is set.

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

For one-off snippets you can use Playwright directly. For multi-step
interactions, prefer `scripts/interact.py` (see *Form Interaction* below),
which accepts a JSON step file and returns a structured report.

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

## Form Interaction

Use `scripts/interact.py` to drive multi-step flows (login, fill, submit,
screenshot, extract) without writing inline Python. Steps are declared in a
JSON file; the script returns a JSON report describing each step plus any
values captured via `output_key`.

**Supported actions**: `goto`, `fill`, `click`, `wait_for`, `screenshot`,
`extract` (grabs `inner_text`), `evaluate` (runs JS in the page).

**Example `steps.json`**:

```json
[
  {"action": "goto", "url": "https://httpbin.org/forms/post"},
  {"action": "fill", "selector": "input[name=custname]", "value": "Alice"},
  {"action": "click", "selector": "input[value=large]"},
  {"action": "extract", "selector": "legend", "output_key": "form_title"},
  {"action": "screenshot", "path": "after.png"},
  {"action": "click", "selector": "button"},
  {"action": "wait_for", "selector": "body", "timeout": 10000}
]
```

**Invoke**:

```bash
python3 scripts/interact.py --steps steps.json
python3 scripts/interact.py --url https://example.com --steps steps.json --output result.json
```

**Report shape**:

```json
{
  "status": "ok",
  "failed_at": null,
  "steps": [{"index": 0, "action": "goto", "status": "ok", "url": "..."}],
  "outputs": {"form_title": "Pizza Size"}
}
```

On failure, `status` becomes `"error"`, `failed_at` points to the failing
step index, and the matching step record includes `error_type` + `error`.
The process exits 0 on success, 1 on any step failure.

## Scripts Reference

| Script | Purpose |
|---|---|
| `browse.py` | Navigate to a URL, optionally screenshot, return page metadata as JSON |
| `screenshot.py` | Capture screenshots (full page / element / custom viewport) |
| `extract_content.py` | Extract page content as clean Markdown |
| `interact.py` | Run a JSON-defined sequence of browser interactions |

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

### interact.py

Execute a JSON-defined sequence of browser interactions (see *Form Interaction* above).

```bash
python3 scripts/interact.py --steps steps.json
python3 scripts/interact.py --url https://site.com/login --steps login.json --output report.json
python3 scripts/interact.py --steps steps.json --viewport-width 1920 --viewport-height 1080
```
