# Changelog

Все заметные изменения в этой ветке (`manus-preset`).

## [Unreleased]

— ничего, ждём фидбэка коллег и реальные кейсы.

## [0.3.0] — 2026-04-27

### Added
- **`SECRETS.md`** — сводный гайд по credentials, Docker и system deps по всем скилам
- **`workspace/.env.example`** — шаблон keystore для секретов; реальный `.env` gitignored
- **`workspace/TOOLS.md`** — environment notes (path к `.env`, Docker / system services cheatsheet)
- **`CONTRIBUTING.md`** — гайд для добавления новых скилов
- **`workspace/AGENTS.md`**: новая секция «Skills environment» (агент читает `.env` сам, спрашивает только если пусто)
- **`workspace/AGENTS.md`**: новая секция «Local dev deps — install freely» (`brew install`, `pip install`, `docker pull` — без подтверждения)

### Changed
- **`README.md`** — категории скилов сгруппированы по use-case с эмодзи (Для разработки / Для анализа / Для исследований / Для дизайна / Для медиа / Для тестирования / Для самопрокачки)
- **`README.md`** — добавлен TL;DR блок и оглавление в верхней части
- **`workspace/SOUL.md`** — добавлены exception в «Long Autonomy» («missing deps/keys = ask, не park в todo») и правило в «Skills-First Mindset» («missing tools = ask the human, не burn the skill»)

### Removed
- **`skills/slk/`** — Slack skill вычищен (требовал desktop-сессию, OAuth-кейс)
- **`skills/gmail/`** — Gmail skill вычищен (managed OAuth слишком тяжёлая зависимость)
- **`skills/google-calendar/`** — Google Calendar skill вычищен (полноценный OAuth flow)

Итого пресет: **19 скилов** (было 22).

## [0.2.0] — 2026-04-27

### Added
- **`workspace/AGENTS.md`** (canonical OpenClaw bootstrap basename) — operating rules с Skills Protocol и Long-Task Workflow
- **`workspace/SOUL.md`** — mindset с Long Autonomy и Skills-First Mindset
- **`workspace/AGENTS.md`** — секция «Missing deps or keys — ask, don't improvise» (агент стопает и спрашивает вместо silent fallback на curl/exec)
- **`workspace/SOUL.md`** — exception к «park doubt, move» правилу для missing deps/keys

### Changed
- **Repo layout**: 22 папки скилов перемещены из корня в `skills/`; bootstrap файлы лежат в `workspace/`
- **`README.md`** — переписан install-флоу: two-step `cp` + restart; conflict warning для существующих `AGENTS.md`/`SOUL.md`

## [0.1.0] — earlier

Original valery skill set + ClawHub community + Anthropic skills (см. Credits в README).
