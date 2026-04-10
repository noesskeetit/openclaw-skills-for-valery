---
name: web-search-searxng
description: "Use this skill when you need to search the internet for current information, news, documentation, or answers to factual questions. Returns ranked results from Google, Bing, DuckDuckGo, Wikipedia and other engines. Powered by SearXNG — a self-hosted meta-search engine. Free, no API keys, no limits."
license: MIT
---

# Web Search (SearXNG)

## Overview

Search the internet via self-hosted SearXNG instance. Aggregates results from Google, Bing, DuckDuckGo, Wikipedia and 70+ other search engines. Free, no API keys, no rate limits.

## Prerequisites

SearXNG must be running. Start with docker-compose:

```bash
cd web-search-searxng
docker compose up -d
```

Default endpoint: `http://localhost:8080`

## Usage

```bash
export SEARXNG_URL=http://localhost:8080
python scripts/search.py "your query here"
python scripts/search.py "Cloud.ru AI" --max-results 10
python scripts/search.py "kubernetes news" --categories news
python scripts/search.py "Python tutorial" --language ru
```

## Output

```json
[
  {
    "title": "Page Title",
    "url": "https://example.com/page",
    "snippet": "Brief description...",
    "source": "google"
  }
]
```

## Categories

| Category | What it searches |
|----------|-----------------|
| `general` | Web pages (default) |
| `news` | News articles |
| `science` | Academic papers |
| `images` | Images |
| `videos` | Videos |
| `it` | Tech/IT resources |

## When to Use

- **Web Search** — "What is X?", "Latest news about Y" → this skill
- **Web Fetch** — You have a URL, want to read content → WebFetch tool
- **Web Browser** — Need JS rendering, forms, screenshots → web-browser skill
