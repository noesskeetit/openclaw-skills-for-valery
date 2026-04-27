#!/usr/bin/env python3
"""Browse a URL, optionally take screenshot, return page info."""
import argparse
import json
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description='Browse URL with Playwright')
    parser.add_argument('url', help='URL to navigate to')
    parser.add_argument('--screenshot', help='Save screenshot to this path')
    parser.add_argument('--wait', default='networkidle',
                        choices=['load', 'domcontentloaded', 'networkidle', 'commit'])
    parser.add_argument('--timeout', type=int, default=30000,
                        help='Navigation timeout in ms')
    parser.add_argument('--viewport-width', type=int, default=1280)
    parser.add_argument('--viewport-height', type=int, default=720)
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': args.viewport_width, 'height': args.viewport_height}
        )
        page.goto(args.url, wait_until=args.wait, timeout=args.timeout)

        if args.screenshot:
            page.screenshot(path=args.screenshot, full_page=True)

        result = {
            "title": page.title(),
            "url": page.url,
            "html_length": len(page.content()),
        }
        browser.close()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
