#!/usr/bin/env python3
"""Execute a sequence of browser interactions from a JSON step file.

Reads a JSON array of steps, runs them against a fresh browser session,
and emits a JSON report describing the outcome of each step plus any
values captured via `extract` / `evaluate` steps.

Supported actions:
    goto        {"action": "goto", "url": "https://..."}
    fill        {"action": "fill", "selector": "#id", "value": "text"}
    click       {"action": "click", "selector": "button"}
    wait_for    {"action": "wait_for", "selector": ".ready", "timeout": 5000}
    screenshot  {"action": "screenshot", "path": "out.png", "full_page": true}
    extract     {"action": "extract", "selector": "h1", "output_key": "title"}
    evaluate    {"action": "evaluate", "script": "document.title", "output_key": "t"}

The overall exit code is 0 if every step succeeds, 1 otherwise.
"""
import argparse
import json
import sys
import traceback
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright


DEFAULT_TIMEOUT = 30000


def run_step(page, step: dict, index: int, outputs: dict) -> dict:
    """Execute a single step and return its status record."""
    action = step.get("action")
    record: dict[str, Any] = {"index": index, "action": action, "status": "ok"}
    timeout = int(step.get("timeout", DEFAULT_TIMEOUT))

    if action == "goto":
        url = step["url"]
        wait = step.get("wait_until", "networkidle")
        page.goto(url, wait_until=wait, timeout=timeout)
        record["url"] = page.url

    elif action == "fill":
        page.fill(step["selector"], step["value"], timeout=timeout)
        record["selector"] = step["selector"]

    elif action == "click":
        page.click(step["selector"], timeout=timeout)
        record["selector"] = step["selector"]

    elif action == "wait_for":
        page.wait_for_selector(step["selector"], timeout=timeout)
        record["selector"] = step["selector"]

    elif action == "screenshot":
        path = step["path"]
        page.screenshot(path=path, full_page=bool(step.get("full_page", False)))
        record["path"] = path

    elif action == "extract":
        selector = step["selector"]
        element = page.query_selector(selector)
        if element is None:
            raise RuntimeError(f"selector {selector!r} not found")
        value = element.inner_text()
        record["selector"] = selector
        record["value"] = value
        key = step.get("output_key")
        if key:
            outputs[key] = value
            record["output_key"] = key

    elif action == "evaluate":
        script = step["script"]
        value = page.evaluate(script)
        record["value"] = value
        key = step.get("output_key")
        if key:
            outputs[key] = value
            record["output_key"] = key

    else:
        raise ValueError(f"unknown action: {action!r}")

    return record


def main():
    parser = argparse.ArgumentParser(
        description="Run a sequence of browser interactions defined in JSON."
    )
    parser.add_argument("--url", help="Initial URL (prepended as a goto step)")
    parser.add_argument(
        "--steps", required=True, help="Path to JSON file with list of steps"
    )
    parser.add_argument(
        "--output",
        help="Write final JSON report to this path (default: stdout)",
    )
    parser.add_argument(
        "--viewport-width", type=int, default=1280, help="Viewport width (default 1280)"
    )
    parser.add_argument(
        "--viewport-height", type=int, default=720, help="Viewport height (default 720)"
    )
    parser.add_argument(
        "--headed", action="store_true", help="Launch a headed browser (debug)"
    )
    args = parser.parse_args()

    with open(args.steps, "r", encoding="utf-8") as f:
        steps = json.load(f)

    if not isinstance(steps, list):
        print("Error: steps file must contain a JSON array", file=sys.stderr)
        sys.exit(2)

    if args.url:
        steps = [{"action": "goto", "url": args.url}] + steps

    outputs: dict[str, Any] = {}
    records: list[dict[str, Any]] = []
    overall_status = "ok"
    failure_index: int | None = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_page(
            viewport={"width": args.viewport_width, "height": args.viewport_height}
        )
        for i, step in enumerate(steps):
            try:
                records.append(run_step(page, step, i, outputs))
            except (PlaywrightTimeout, PlaywrightError, RuntimeError, KeyError, ValueError) as exc:
                overall_status = "error"
                failure_index = i
                records.append(
                    {
                        "index": i,
                        "action": step.get("action"),
                        "status": "error",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )
                break
            except Exception as exc:  # noqa: BLE001 - surface unexpected errors
                overall_status = "error"
                failure_index = i
                records.append(
                    {
                        "index": i,
                        "action": step.get("action"),
                        "status": "error",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                )
                break
        browser.close()

    report = {
        "status": overall_status,
        "failed_at": failure_index,
        "steps": records,
        "outputs": outputs,
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"Report saved to {args.output}")
    else:
        print(payload)

    sys.exit(0 if overall_status == "ok" else 1)


if __name__ == "__main__":
    main()
