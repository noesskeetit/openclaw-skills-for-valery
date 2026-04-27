#!/usr/bin/env python3
"""Take screenshots of web pages with fine-grained control.

Supports full-page capture, element-based cropping via CSS selectors,
and custom viewport dimensions.
"""
import argparse
import sys
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(
        description='Take screenshots of web pages with Playwright'
    )
    parser.add_argument('url', help='URL to capture')
    parser.add_argument('-o', '--output', default='screenshot.png',
                        help='Output file path (default: screenshot.png)')
    parser.add_argument('--selector', help='CSS selector to capture specific element')
    parser.add_argument('--full-page', action='store_true',
                        help='Capture the full scrollable page')
    parser.add_argument('--wait', default='networkidle',
                        choices=['load', 'domcontentloaded', 'networkidle', 'commit'],
                        help='Wait condition before screenshot (default: networkidle)')
    parser.add_argument('--timeout', type=int, default=30000,
                        help='Navigation timeout in ms (default: 30000)')
    parser.add_argument('--viewport-width', type=int, default=1280,
                        help='Browser viewport width (default: 1280)')
    parser.add_argument('--viewport-height', type=int, default=720,
                        help='Browser viewport height (default: 720)')
    parser.add_argument('--wait-for-selector', metavar='SELECTOR',
                        help='Wait for this CSS selector before taking screenshot')
    parser.add_argument('--wait-for-timeout', type=int, metavar='MS',
                        help='Wait additional milliseconds before taking screenshot')
    parser.add_argument('--quality', type=int,
                        help='JPEG quality 0-100 (only for .jpg/.jpeg output)')
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': args.viewport_width, 'height': args.viewport_height}
        )
        page.goto(args.url, wait_until=args.wait, timeout=args.timeout)

        if args.wait_for_selector:
            page.wait_for_selector(args.wait_for_selector, timeout=args.timeout)

        if args.wait_for_timeout:
            page.wait_for_timeout(args.wait_for_timeout)

        screenshot_kwargs = {'path': args.output}

        if args.quality is not None:
            if not args.output.lower().endswith(('.jpg', '.jpeg')):
                print("Error: --quality is only supported for JPEG output", file=sys.stderr)
                browser.close()
                sys.exit(1)
            screenshot_kwargs['quality'] = args.quality

        if args.selector:
            element = page.query_selector(args.selector)
            if element is None:
                print(f"Error: selector '{args.selector}' not found on page",
                      file=sys.stderr)
                browser.close()
                sys.exit(1)
            element.screenshot(**screenshot_kwargs)
            print(f"Element screenshot saved to {args.output}")
        else:
            screenshot_kwargs['full_page'] = args.full_page
            page.screenshot(**screenshot_kwargs)
            mode = "full-page" if args.full_page else "viewport"
            print(f"Screenshot ({mode}) saved to {args.output}")

        browser.close()


if __name__ == '__main__':
    main()
