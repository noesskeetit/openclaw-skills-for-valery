#!/usr/bin/env python3
"""Search the internet via SearXNG."""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error


def search(query, max_results=5, categories="general", language="auto"):
    base_url = os.environ.get("SEARXNG_URL", "http://localhost:8080")

    # Bypass corporate proxy for local SearXNG
    from urllib.parse import urlparse
    host = urlparse(base_url).hostname
    if host in ("localhost", "127.0.0.1", "searxng"):
        os.environ["no_proxy"] = os.environ.get("no_proxy", "") + f",{host}"

    params = {
        "q": query,
        "format": "json",
        "categories": categories,
    }
    if language != "auto":
        params["language"] = language

    url = f"{base_url}/search?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; OpenClaw/1.0)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Cannot reach SearXNG at {base_url}: {e}"}), file=sys.stderr)
        sys.exit(1)

    results = []
    for item in data.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "source": item.get("engine", ""),
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search the internet via SearXNG")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--categories", default="general",
                        choices=["general", "news", "science", "images", "videos", "it"],
                        help="Search category (default: general)")
    parser.add_argument("--language", default="auto", help="Language code, e.g. ru, en (default: auto)")
    args = parser.parse_args()

    results = search(args.query, args.max_results, args.categories, args.language)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
