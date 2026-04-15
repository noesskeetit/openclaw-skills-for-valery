---
name: web-search-searxng
description: "Use this skill when you need to search the internet for current information, news, documentation, or answers to factual questions. Returns ranked results from Google, Bing, DuckDuckGo, Wikipedia and other engines. Powered by SearXNG — a self-hosted meta-search engine. Free, no API keys, no limits."
license: MIT
---

# Web Search (SearXNG)

## Overview

Search the internet via self-hosted SearXNG instance. Aggregates results from Google, Bing, DuckDuckGo, Wikipedia and 70+ other search engines. Free, no API keys, no rate limits.

## Prerequisites

- Skill will automatically start its SearXNG container via `docker compose up -d` on first invocation (from the skill's own directory).
- Requires docker daemon access. If docker is unavailable, use the `web-search-tavily` skill instead.
- Works out of the box — no manual setup required.

Default endpoint: `http://localhost:8080` (override with `SEARXNG_URL`).

## Usage

```bash
python3 scripts/search.py "your query here"
python3 scripts/search.py "Cloud.ru AI" --max-results 10
python3 scripts/search.py "kubernetes news" --categories news
python3 scripts/search.py "Python tutorial" --language ru
```

Flags:
- `--max-results N` — cap result count (default: 5)
- `--categories {general,news,science,images,videos,it}` — search scope
- `--language <code>` — e.g. `ru`, `en` (default: `auto`)
- `--no-auto-start` — don't try to bring up the container; fail fast if service is down

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

## Troubleshooting

- **Docker unavailable / no permission:** the script returns a JSON error to stderr and exits non-zero. Start Docker Desktop, grant socket access.
- **Check status:** `cd` into the skill directory and run `docker compose ps` — a healthy container shows `(healthy)`.
- **View logs:** `docker compose logs -f searxng` from the skill directory.
- **Stop the service:** `docker compose down` from the skill directory.
- **Restart after config change:** `docker compose up -d --force-recreate`.
- **Resource footprint:** ~200–300 MB RAM idle, capped at 512 MB via `mem_limit`.
- **Custom endpoint:** set `SEARXNG_URL=http://host:port`; auto-start only kicks in for `localhost`/`127.0.0.1`.
