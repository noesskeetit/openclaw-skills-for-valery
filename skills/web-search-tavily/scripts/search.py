#!/usr/bin/env python3
"""Search the internet via Tavily API."""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def search(query, max_results=5, categories="general", timeout=15):
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        print(json.dumps({"error": "TAVILY_API_KEY not set"}), file=sys.stderr)
        sys.exit(1)

    body = json.dumps({
        "query": query,
        "max_results": max_results,
        "topic": "news" if categories == "news" else "general",
        "include_answer": True,
    }).encode()

    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"Tavily API error: {e.code} {e.reason}"}), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Tavily connection error: {e}"}), file=sys.stderr)
        sys.exit(1)

    results = []

    answer = data.get("answer")
    if answer:
        results.append({
            "title": "AI Summary",
            "url": "",
            "snippet": answer,
            "source": "tavily",
        })

    for item in data.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "source": "tavily",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search the internet via Tavily API")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--categories", default="general",
                        choices=["general", "news"],
                        help="Search category (default: general)")
    parser.add_argument("--timeout", type=int, default=15,
                        help="HTTP timeout in seconds (default: 15)")
    args = parser.parse_args()

    results = search(args.query, args.max_results, args.categories, args.timeout)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
