#!/usr/bin/env python3
"""Extract page content and convert to clean markdown.

Navigates to a URL with a real browser, strips non-content elements
(nav, footer, ads, scripts, styles), and converts the remaining HTML
to well-formatted markdown using markdownify.
"""
import argparse
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Elements to remove before content extraction
STRIP_TAGS = [
    'script', 'style', 'noscript', 'iframe',
    'nav', 'footer', 'header',
    'aside',
]

STRIP_SELECTORS = [
    '[role="navigation"]',
    '[role="banner"]',
    '[role="contentinfo"]',
    '[aria-hidden="true"]',
    '.nav', '.navbar', '.navigation',
    '.footer', '.site-footer',
    '.sidebar', '.side-bar',
    '.ad', '.ads', '.advertisement', '.adsbygoogle',
    '.cookie-banner', '.cookie-notice', '.cookie-consent',
    '#cookie-banner', '#cookie-notice',
    '.popup', '.modal',
    '.social-share', '.share-buttons',
]


def clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove non-content elements from the parsed HTML."""
    for tag_name in STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for selector in STRIP_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    return soup


def html_to_markdown(html: str, base_url: str = '') -> str:
    """Convert HTML to clean markdown, stripping non-content elements."""
    soup = BeautifulSoup(html, 'lxml')
    soup = clean_html(soup)

    markdown = md(
        str(soup),
        heading_style='ATX',
        bullets='-',
        strip=['img', 'script', 'style', 'svg', 'iframe'],
    )

    # Clean up excessive whitespace
    lines = markdown.split('\n')
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        stripped = line.rstrip()
        is_empty = len(stripped) == 0
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(stripped)
        prev_empty = is_empty

    result = '\n'.join(cleaned_lines).strip()
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Extract web page content as clean markdown'
    )
    parser.add_argument('url', help='URL to extract content from')
    parser.add_argument('-o', '--output', help='Save markdown to file instead of stdout')
    parser.add_argument('--selector', default='body',
                        help='CSS selector for content area (default: body)')
    parser.add_argument('--wait', default='networkidle',
                        choices=['load', 'domcontentloaded', 'networkidle', 'commit'],
                        help='Wait condition before extraction (default: networkidle)')
    parser.add_argument('--timeout', type=int, default=30000,
                        help='Navigation timeout in ms (default: 30000)')
    parser.add_argument('--viewport-width', type=int, default=1280)
    parser.add_argument('--viewport-height', type=int, default=720)
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': args.viewport_width, 'height': args.viewport_height}
        )
        page.goto(args.url, wait_until=args.wait, timeout=args.timeout)

        element = page.query_selector(args.selector)
        if element is None:
            print(f"Error: selector '{args.selector}' not found on page",
                  file=sys.stderr)
            browser.close()
            sys.exit(1)

        html = element.inner_html()
        browser.close()

    markdown = html_to_markdown(html, base_url=args.url)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Content saved to {args.output}")
    else:
        print(markdown)


if __name__ == '__main__':
    main()
