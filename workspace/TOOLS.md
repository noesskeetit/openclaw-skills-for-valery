# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Skills environment — `.env`

Все API keys / credentials для скилов в этом пресете живут в одном файле:

**`~/.openclaw/workspace/.env`** — простой dotenv формат `KEY=value`. Файл не комитится (gitignored). Чтобы посмотреть что есть:

```bash
cat ~/.openclaw/workspace/.env
```

Известные переменные пресета:
- `TAVILY_API_KEY` — для `web-search-tavily`
- `MATON_API_KEY` — для `gmail`
- `GOOGLE_OAUTH_CREDS_PATH` — путь до `credentials.json` для `google-calendar`

Skill `web-search-searxng` требует запущенного Docker — см. ниже.

## Docker / system services

- **Docker Desktop** — для `web-search-searxng` (запускает свой SearXNG контейнер)
- **Playwright + Chromium** — `playwright install chromium` (для `web-browser`, `webapp-testing`)
- **System packages** (через `brew install`): `tesseract`, `graphviz`, `poppler`, `ghostscript`, `imagemagick`, `libreoffice` — нужны разным скилам, см. AGENTS.md «Local dev deps»

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
