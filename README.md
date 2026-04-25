# OpenClaw Skills — Manus Preset

A curated skill pack that turns an OpenClaw (or compatible) agent into a general-purpose assistant covering most common user scenarios out of the box. Sources: the original valery skill set + Anthropic's official `anthropics/skills` + ClawHub community skills + a skill-discovery fallback.

Target audience: **regular end users** (office, content, creative, communications) and **developers** (code, APIs, databases, MCPs). Each skill is a self-contained folder with a `SKILL.md`; no Docker gateway, no external runtime — just markdown + scripts.

## Skills (22)

### Documents & data

| Skill | Purpose |
|---|---|
| [document-analyzer](./document-analyzer) | Read/extract/OCR PDF, DOCX, XLSX, PPTX, CSV; PDF form filling |
| [document-creator](./document-creator) | Create DOCX, XLSX, PPTX, PDF with OOXML validation |
| [sql-toolkit](./sql-toolkit) | SQLite/PostgreSQL/MySQL — schema design, queries, migrations, indexing, backup/restore |

### Code & development

| Skill | Purpose |
|---|---|
| [code-runner](./code-runner) | Execute Python / JavaScript with stdout/stderr/file capture |
| [git-assistant](./git-assistant) | Commits, code review, PR descriptions |
| [api-tester](./api-tester) | Structured HTTP/HTTPS requests (GET/POST/PUT/DELETE) with custom headers + JSON |
| [mcp-builder](./mcp-builder) | Build MCP servers in Python (FastMCP) or TypeScript (MCP SDK) |
| [skill-creator](./skill-creator) | Create/modify/benchmark skills; meta-skill |

### Web & search

| Skill | Purpose |
|---|---|
| [web-browser](./web-browser) | Playwright browser automation (SPA, forms, screenshots) |
| [web-search-searxng](./web-search-searxng) | Self-hosted meta-search (SearXNG, Docker-based) |
| [web-search-tavily](./web-search-tavily) | AI-optimized search via Tavily API |
| [webapp-testing](./webapp-testing) | Playwright e2e testing for local webapps |

### Design & content

| Skill | Purpose |
|---|---|
| [frontend-design](./frontend-design) | Production-grade UI (React/HTML/CSS), avoids generic AI aesthetic |
| [web-artifacts-builder](./web-artifacts-builder) | React + Tailwind + shadcn/ui multi-component artifacts |
| [diagram-generator](./diagram-generator) | Mermaid + Graphviz → SVG/PNG/PDF |
| [theme-factory](./theme-factory) | Apply themes (10 presets + custom) to slides/docs/landings |
| [doc-coauthoring](./doc-coauthoring) | Structured workflow for collaborative docs (proposals, PRDs, RFCs, specs) |

### Communications

| Skill | Purpose |
|---|---|
| [gmail](./gmail) | Read/send/manage Gmail emails, threads, labels, drafts (managed OAuth) |
| [google-calendar](./google-calendar) | List/create/update/delete calendar events via Google Calendar API |
| [slk](./slk) | Read/send/search/manage Slack messages and DMs via `slk` CLI |

### Media

| Skill | Purpose |
|---|---|
| [vision](./vision) | Image processing — resize, crop, convert (PNG/WebP), compress, watermark via ImageMagick |

### Meta

| Skill | Purpose |
|---|---|
| [find-skills](./find-skills) | Discover and install additional skills from `skills.sh` registry when a capability is missing |

## Skill format

```
skill-name/
├── SKILL.md           # YAML frontmatter + instructions for the agent
├── requirements.txt   # Python deps (when applicable)
├── scripts/           # executables the agent invokes (optional)
└── references/        # supplementary docs (optional)
```

```yaml
---
name: skill-name
description: "When to use this skill, what it does, what it does NOT do."
license: MIT
---
```

The `description` is what the agent reads to decide when to invoke the skill. The body explains how to use the scripts.

## Install

```bash
# Clone
git clone https://github.com/noesskeetit/openclaw-skills-for-valery.git
cd openclaw-skills-for-valery
git checkout manus-preset

# Copy all skills into the OpenClaw workspace
cp -R */ ~/.openclaw/workspace/skills/

# Restart the gateway so it picks up new skills
openclaw gateway restart

# Verify
openclaw skills list
```

Per-skill setup (system deps / Python envs / API keys / OAuth flows) is documented in each `SKILL.md`. Skills requiring external credentials:

- `gmail` — `MATON_API_KEY` (managed OAuth via Maton)
- `google-calendar` — Google OAuth credentials
- `slk` — Slack workspace auth via `slk` CLI
- `web-search-tavily` — `TAVILY_API_KEY`

## How this works (the "Manus" pattern)

The agent loads all skills at session start and each skill's `description` acts as a trigger. When a user asks something that matches a skill, the agent invokes it. If nothing matches, the agent falls back to `find-skills` which queries the public `skills.sh` registry and can install a new skill on the fly.

This gives Manus-like breadth without locking the agent into a single vendor or long-running autonomous mode.

## Resource footprint

Designed to coexist on a small VM (≥2 GB RAM, ~10 GB disk). Heaviest skills:

- **web-browser / webapp-testing** — ~375 MB RAM per Chromium session
- **diagram-generator** — up to ~1 GB during Mermaid render
- **document-analyzer** — up to ~1 GB on large PDFs with OCR
- **web-search-searxng** — ~200-300 MB resident as background container

Run heavy skills serially on constrained hardware.

## Adding a new skill

1. Create `your-skill/` with `SKILL.md` and any scripts
2. Fill the YAML frontmatter (`name`, `description`, `license`)
3. Make `description` tell the agent **when** and **when NOT** to use the skill
4. Document each script's CLI in `SKILL.md`
5. Open a PR against `manus-preset`

## Credits

- **Original 8 skills** (`code-runner`, `diagram-generator`, `document-analyzer`, `document-creator`, `git-assistant`, `web-browser`, `web-search-searxng`, `web-search-tavily`) — from the `main` branch of this repo
- **Anthropic skills** (`frontend-design`, `webapp-testing`, `skill-creator`, `mcp-builder`, `web-artifacts-builder`, `theme-factory`, `doc-coauthoring`) — from [anthropics/skills](https://github.com/anthropics/skills)
- **ClawHub community skills** (`gmail`, `google-calendar`, `slk`, `vision`, `sql-toolkit`, `api-tester`) — from [clawhub.ai](https://clawhub.ai/) (each retains its original license)
- **find-skills** — discovery helper around [skills.sh](https://skills.sh/) CLI

## License

Each skill carries its own license file. Original `code-runner`, `document-*`, `web-*` skills are MIT (see [LICENSE](./LICENSE)). Third-party skills carry their respective licenses inside each skill folder.
