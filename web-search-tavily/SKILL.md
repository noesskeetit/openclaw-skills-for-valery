---
name: web-search-tavily
description: "Use this skill when you need to search the internet for current information, news, documentation, or answers to factual questions. Returns ranked results with titles, URLs, and snippets plus an AI-generated summary. Powered by Tavily — an AI-optimized search API. Free: 1000 requests/month."
license: MIT
---

# Web Search (Tavily)

## Prerequisites

```bash
export TAVILY_API_KEY=tvly-your-key-here
```

Get your free key at https://tavily.com (30 seconds, no credit card).

## Usage

```bash
python scripts/search.py "your query here"
python scripts/search.py "Cloud.ru AI" --max-results 10
python scripts/search.py "kubernetes latest news" --categories news
python scripts/search.py "machine learning papers" --language en
```

## Output

```json
[
  {
    "title": "AI Summary",
    "url": "",
    "snippet": "AI-generated answer based on search results...",
    "source": "tavily"
  },
  {
    "title": "Page Title",
    "url": "https://example.com/page",
    "snippet": "Brief description...",
    "source": "tavily"
  }
]
```

## Categories

| Category | Tavily topic |
|----------|-------------|
| `general` | General web (default) |
| `news` | News articles |

## When to Use

- **Web Search** — "What is X?", "Latest news about Y" → this skill
- **Web Fetch** — You have a URL, want to read content → WebFetch tool
- **Web Browser** — Need JS rendering, forms, screenshots → web-browser skill
