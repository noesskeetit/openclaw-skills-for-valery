# OpenClaw Skills — Manus Preset

A curated skill pack **plus** workspace bootstrap that flips an OpenClaw agent onto **Manus-style rails**: skills-first dispatch, long-task autonomy, todo-driven workflow. Sources: the original valery skill set + Anthropic's official `anthropics/skills` + ClawHub community skills + a skill-discovery fallback.

Target audience: **regular end users** (office, content, creative, communications) and **developers** (code, APIs, databases, MCPs). Each skill is a self-contained folder with a `SKILL.md`; the bootstrap is two markdown files. No Docker gateway, no install scripts — just files you copy where you need them.

## Repo layout

```
openclaw-skills-for-valery/
├── workspace/         # Bootstrap that switches OpenClaw onto Manus rails
│   ├── AGENTS.md      # Operating rules: Skills Protocol + Long-Task Workflow
│   └── SOUL.md        # Mindset: Long Autonomy + Skills-First reflex
├── skills/            # 22 skills (each a self-contained folder with SKILL.md)
└── README.md
```

The two folders mirror the layout of `~/.openclaw/workspace/` so you can drop them in directly, or you can cherry-pick whatever you want and integrate the way that fits your setup.

## Skills (22)

### Documents & data

| Skill | Purpose |
|---|---|
| [document-analyzer](./skills/document-analyzer) | Read/extract/OCR PDF, DOCX, XLSX, PPTX, CSV; PDF form filling |
| [document-creator](./skills/document-creator) | Create DOCX, XLSX, PPTX, PDF with OOXML validation |
| [sql-toolkit](./skills/sql-toolkit) | SQLite/PostgreSQL/MySQL — schema design, queries, migrations, indexing, backup/restore |

### Code & development

| Skill | Purpose |
|---|---|
| [code-runner](./skills/code-runner) | Execute Python / JavaScript with stdout/stderr/file capture |
| [git-assistant](./skills/git-assistant) | Commits, code review, PR descriptions |
| [api-tester](./skills/api-tester) | Structured HTTP/HTTPS requests (GET/POST/PUT/DELETE) with custom headers + JSON |
| [mcp-builder](./skills/mcp-builder) | Build MCP servers in Python (FastMCP) or TypeScript (MCP SDK) |
| [skill-creator](./skills/skill-creator) | Create/modify/benchmark skills; meta-skill |

### Web & search

| Skill | Purpose |
|---|---|
| [web-browser](./skills/web-browser) | Playwright browser automation (SPA, forms, screenshots) |
| [web-search-searxng](./skills/web-search-searxng) | Self-hosted meta-search (SearXNG, Docker-based) |
| [web-search-tavily](./skills/web-search-tavily) | AI-optimized search via Tavily API |
| [webapp-testing](./skills/webapp-testing) | Playwright e2e testing for local webapps |

### Design & content

| Skill | Purpose |
|---|---|
| [frontend-design](./skills/frontend-design) | Production-grade UI (React/HTML/CSS), avoids generic AI aesthetic |
| [web-artifacts-builder](./skills/web-artifacts-builder) | React + Tailwind + shadcn/ui multi-component artifacts |
| [diagram-generator](./skills/diagram-generator) | Mermaid + Graphviz → SVG/PNG/PDF |
| [theme-factory](./skills/theme-factory) | Apply themes (10 presets + custom) to slides/docs/landings |
| [doc-coauthoring](./skills/doc-coauthoring) | Structured workflow for collaborative docs (proposals, PRDs, RFCs, specs) |

### Communications

| Skill | Purpose |
|---|---|
| [gmail](./skills/gmail) | Read/send/manage Gmail emails, threads, labels, drafts (managed OAuth) |
| [google-calendar](./skills/google-calendar) | List/create/update/delete calendar events via Google Calendar API |
| [slk](./skills/slk) | Read/send/search/manage Slack messages and DMs via `slk` CLI |

### Media

| Skill | Purpose |
|---|---|
| [vision](./skills/vision) | Image processing — resize, crop, convert (PNG/WebP), compress, watermark via ImageMagick |

### Meta

| Skill | Purpose |
|---|---|
| [find-skills](./skills/find-skills) | Discover and install additional skills from `skills.sh` registry when a capability is missing |

## What's in the bootstrap

Two files, ~200 lines combined. Together they switch a default OpenClaw onto Manus rails.

- **[`workspace/AGENTS.md`](./workspace/AGENTS.md)** (~140 lines) — operating rules. The big new section is **Skills Protocol**: dispatch order, default reflex ("before writing curl, check whether a skill does it"), conflict-pair guidance (`searxng` vs `tavily` etc.), escape hatches (`find-skills`, `skill-creator`). The other big section is **Long-Task Workflow**: sticky `memory/todo.md`, file-as-memory in `memory/scratch/`, leave-wrong-turns markers, checkpointing after big moves. Red Lines and External-vs-Internal are kept from the canonical OpenClaw template.
- **[`workspace/SOUL.md`](./workspace/SOUL.md)** (~60 lines) — mindset. **Long Autonomy** (default to keep going on long tasks, park doubts in todo, file-as-memory) and **Skills-First Mindset** (inventory awareness, read SKILL.md before improvising, two escape hatches) are the new sections. Core Truths, Boundaries, Continuity are inherited from the template.

The other five canonical OpenClaw bootstrap files (`BOOTSTRAP.md`, `IDENTITY.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`) are intentionally **not** part of the preset — they're personal / environment-specific and the user fills them in themselves.

## Install

Two `cp` commands and a gateway restart. Nothing fancier — that's by design.

```bash
git clone https://github.com/noesskeetit/openclaw-skills-for-valery.git
cd openclaw-skills-for-valery
git checkout manus-preset

# 1. Copy all skills into the OpenClaw workspace
cp -R skills/. ~/.openclaw/workspace/skills/

# 2. Copy the two bootstrap files into the workspace root
cp workspace/AGENTS.md workspace/SOUL.md ~/.openclaw/workspace/

# 3. Restart the gateway so it picks up new skills
openclaw gateway restart

# 4. Verify
openclaw skills list
```

### ⚠️ Conflict warning

Step 2 will **overwrite** any existing `~/.openclaw/workspace/AGENTS.md` and `~/.openclaw/workspace/SOUL.md` (the ones `openclaw setup` creates by default).

If you've already customised them, back them up first:

```bash
cp ~/.openclaw/workspace/AGENTS.md ~/.openclaw/workspace/AGENTS.md.bak
cp ~/.openclaw/workspace/SOUL.md ~/.openclaw/workspace/SOUL.md.bak
```

…then either replace or merge by hand. The "What's in the bootstrap" section above is a quick map of the new sections so you know what to splice in.

### Per-skill setup (env / OAuth / system deps)

Each skill's `SKILL.md` has the details. Skills requiring credentials:

- `gmail` — `MATON_API_KEY` (managed OAuth via Maton)
- `google-calendar` — Google OAuth credentials
- `slk` — Slack workspace auth via `slk` CLI
- `web-search-tavily` — `TAVILY_API_KEY`

`openclaw skills list` shows ready vs needs-setup at a glance.

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

## How this works (the "Manus" pattern)

The agent loads `AGENTS.md` and `SOUL.md` at session start. They tell it the **default reflex** is to check `skills/` before writing code, to use `openclaw skills list` to compare similar skills, and to fall back to `find-skills` when nothing matches. Each skill's `description` in `SKILL.md` acts as the trigger.

For long tasks the agent maintains `memory/todo.md` as sticky context, dumps heavy intermediate state into `memory/scratch/`, marks `WRONG_TURN:` lines for dead-ends, and checkpoints after big moves — that's the autonomy half of the preset.

Together: skills give Manus-like breadth, the bootstrap gives Manus-like discipline.

## Resource footprint

Designed to coexist on a small VM (≥2 GB RAM, ~10 GB disk). Heaviest skills:

- **web-browser / webapp-testing** — ~375 MB RAM per Chromium session
- **diagram-generator** — up to ~1 GB during Mermaid render
- **document-analyzer** — up to ~1 GB on large PDFs with OCR
- **web-search-searxng** — ~200-300 MB resident as background container

Run heavy skills serially on constrained hardware.

## Updating

```bash
cd openclaw-skills-for-valery
git pull
cp -R skills/. ~/.openclaw/workspace/skills/
cp workspace/AGENTS.md workspace/SOUL.md ~/.openclaw/workspace/
openclaw gateway restart
```

If you've customised the bootstrap files locally, back them up before re-copying.

## Adding a new skill

1. Create `skills/your-skill/` with `SKILL.md` and any scripts
2. Fill the YAML frontmatter (`name`, `description`, `license`)
3. Make `description` tell the agent **when** and **when NOT** to use the skill
4. Document each script's CLI in `SKILL.md`
5. Open a PR against `manus-preset`

## Credits

- **Original 8 skills** (`code-runner`, `diagram-generator`, `document-analyzer`, `document-creator`, `git-assistant`, `web-browser`, `web-search-searxng`, `web-search-tavily`) — from the `main` branch of this repo
- **Anthropic skills** (`frontend-design`, `webapp-testing`, `skill-creator`, `mcp-builder`, `web-artifacts-builder`, `theme-factory`, `doc-coauthoring`) — from [anthropics/skills](https://github.com/anthropics/skills)
- **ClawHub community skills** (`gmail`, `google-calendar`, `slk`, `vision`, `sql-toolkit`, `api-tester`) — from [clawhub.ai](https://clawhub.ai/) (each retains its original license)
- **find-skills** — discovery helper around [skills.sh](https://skills.sh/) CLI
- **Bootstrap pattern** — informed by the canonical OpenClaw workspace templates (`docs/reference/templates/AGENTS.md`, `SOUL.md`) and the Manus.im operating principles

## License

Each skill carries its own license file. Original `code-runner`, `document-*`, `web-*` skills are MIT (see [LICENSE](./LICENSE)). Third-party skills carry their respective licenses inside each skill folder. Bootstrap files (`workspace/AGENTS.md`, `workspace/SOUL.md`) are MIT.
