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

## Skills (21) — by use case

Группировка по сценариям пользователя, а не по технологии. Большинство скилов работает «из коробки», некоторые требуют ключей или Docker — см. [SECRETS.md](./SECRETS.md) для полного списка.

### 🧑‍💻 Для разработки

Кодинг, API, Git, MCP-серверы, расширение собственных возможностей.

| Skill | Что делает |
|---|---|
| [code-runner](./skills/code-runner) | Выполнить Python / JavaScript, поймать stdout/stderr/files |
| [git-assistant](./skills/git-assistant) | Коммиты с осмысленными сообщениями, ревью diff'ов, PR-описания |
| [api-tester](./skills/api-tester) | Структурные HTTP-запросы (GET/POST/PUT/DELETE) с заголовками и JSON — без ручного `curl` |
| [mcp-builder](./skills/mcp-builder) | Собрать MCP-сервер на Python (FastMCP) или TypeScript (MCP SDK) |
| [skill-creator](./skills/skill-creator) | Создать / отредактировать / прогнать eval'ы по своему скилу — meta-skill |

### 📊 Для анализа и работы с документами

Чтение/создание PDF, DOCX, XLSX, PPTX, работа с SQL.

| Skill | Что делает |
|---|---|
| [document-analyzer](./skills/document-analyzer) | Прочесть / распарсить / OCR-нуть PDF, DOCX, XLSX, PPTX, CSV; заполнить PDF-формы |
| [document-creator](./skills/document-creator) | Создать DOCX, XLSX, PPTX, PDF с валидацией OOXML |
| [sql-toolkit](./skills/sql-toolkit) | SQLite/PostgreSQL/MySQL — схемы, запросы, миграции, индексы, бэкапы |

### 🔍 Для исследований

Поиск, рендеринг JS-страниц, скрейпинг.

| Skill | Что делает |
|---|---|
| [web-search-tavily](./skills/web-search-tavily) | AI-оптимизированный поиск через Tavily API (нужен ключ) |
| [web-search-searxng](./skills/web-search-searxng) | Self-hosted мета-поиск (SearXNG в Docker, без ключей) |
| [web-browser](./skills/web-browser) | Полноценный браузер (Playwright + Chromium) — для SPA, форм, скриншотов |

### 🎨 Для дизайна и контента

Frontend, диаграммы, темизация, совместная работа над текстами.

| Skill | Что делает |
|---|---|
| [frontend-design](./skills/frontend-design) | Production-grade UI (React/HTML/CSS) с дизайн-вкусом, без AI-стандарта |
| [web-artifacts-builder](./skills/web-artifacts-builder) | Мульти-компонентные React + Tailwind + shadcn/ui артефакты |
| [diagram-generator](./skills/diagram-generator) | Mermaid + Graphviz → SVG/PNG/PDF (mind-maps, ER, sequence, flowchart) |
| [theme-factory](./skills/theme-factory) | 10 готовых тем + свои — для слайдов, доков, лендингов |
| [doc-coauthoring](./skills/doc-coauthoring) | Структурный воркфлоу для PRD / RFC / proposal'ов |

### 💬 Для коммуникаций

Почта и календарь — чтение, отправка, управление событиями.

| Skill | Что делает |
|---|---|
| [gmail](./skills/gmail) | Читать / отправлять / искать письма, треды, ярлыки, черновики (managed OAuth, нужен `MATON_API_KEY`) |
| [google-calendar](./skills/google-calendar) | Список / создать / обновить / удалить события (Google OAuth) |

### 🖼️ Для медиа

Изображения.

| Skill | Что делает |
|---|---|
| [vision](./skills/vision) | Resize, crop, конверт (PNG/WebP), сжать, watermark через ImageMagick |

### 🧪 Для тестирования

E2E-тесты локальных веб-приложений.

| Skill | Что делает |
|---|---|
| [webapp-testing](./skills/webapp-testing) | Playwright e2e — кликать, заполнять формы, снимать скриншоты, читать console |

### 🧭 Для самопрокачки агента

Расширение инвентаря.

| Skill | Что делает |
|---|---|
| [find-skills](./skills/find-skills) | Поиск и установка скилов из публичного `skills.sh` registry — когда ничего не подходит |

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

# 3. Create the secrets keystore (keep blank — agent will ask before using a skill that needs a key)
cp workspace/.env.example ~/.openclaw/workspace/.env

# 4. Restart the gateway so it picks up new skills
openclaw gateway restart

# 5. Verify
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

Полный список ключей, OAuth-флоу, Docker и system deps по всем 22 скилам — **[SECRETS.md](./SECRETS.md)**.

TL;DR: всё кладётся в `~/.openclaw/workspace/.env` (template — [`workspace/.env.example`](./workspace/.env.example)). Заполнять заранее не обязательно — агент сам спросит, когда понадобится ключ для конкретного скила (это правило прописано в `workspace/AGENTS.md`).

Скилы, которым нужны credentials:

- `web-search-tavily` — `TAVILY_API_KEY` (бесплатно 1k req/мес на tavily.com)
- `gmail` — `MATON_API_KEY` (managed OAuth via Maton)
- `google-calendar` — Google OAuth `credentials.json`

Скилы, которым нужен **Docker**: `web-search-searxng`. Скилы, которым нужны **system deps** (`tesseract`, `graphviz`, `poppler`, `imagemagick`, `ghostscript`, `pandoc`, …): агент **сам ставит** через `brew install` при необходимости (см. AGENTS.md «Local dev deps — install freely»).

`openclaw skills list` показывает `ready` vs `needs setup` за один взгляд.

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
- **ClawHub community skills** (`gmail`, `google-calendar`, `vision`, `sql-toolkit`, `api-tester`) — from [clawhub.ai](https://clawhub.ai/) (each retains its original license)
- **find-skills** — discovery helper around [skills.sh](https://skills.sh/) CLI
- **Bootstrap pattern** — informed by the canonical OpenClaw workspace templates (`docs/reference/templates/AGENTS.md`, `SOUL.md`) and the Manus.im operating principles

## License

Each skill carries its own license file. Original `code-runner`, `document-*`, `web-*` skills are MIT (see [LICENSE](./LICENSE)). Third-party skills carry their respective licenses inside each skill folder. Bootstrap files (`workspace/AGENTS.md`, `workspace/SOUL.md`) are MIT.
