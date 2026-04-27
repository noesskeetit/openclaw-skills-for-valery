# Skills secrets — what each skill needs

Сводный гайд по credentials, OAuth, Docker и system deps для всех 22 скилов пресета.

## Где хранить

Все API-ключи / paths к credentials живут в одном dotenv-файле:

```
~/.openclaw/workspace/.env
```

Шаблон с placeholder'ами — [`workspace/.env.example`](./workspace/.env.example). Скопируй его на место и заполни известные значения:

```bash
cp workspace/.env.example ~/.openclaw/workspace/.env
$EDITOR ~/.openclaw/workspace/.env
```

Файл `.env` **не комитится** (gitignored). Агент читает его перед тем как использовать скил-кандидат, и если нужного ключа нет — **спросит тебя**, а не свалится в `curl` (см. правило в `workspace/AGENTS.md` секция «Skills environment»).

## Ключи / OAuth

| Скил | Что нужно | Где взять | В `.env` |
|---|---|---|---|
| **`web-search-tavily`** | API key | https://tavily.com — бесплатно 1000 запросов/мес, без карты | `TAVILY_API_KEY=...` |
| **`gmail`** | API key (managed OAuth) | https://maton.ai — Maton управляет OAuth от твоего имени | `MATON_API_KEY=...` |
| **`google-calendar`** | OAuth credentials.json | Google Cloud Console → OAuth 2.0 Client ID → Desktop app → скачай JSON | `GOOGLE_OAUTH_CREDS_PATH=/path/to/credentials.json` |
| **`slk`** | Slack desktop session | Установи Slack desktop, залогинься, потом `slk login` (он вытащит `xoxc-` token из сессии) | — (env не нужен) |

## Docker

| Скил | Что нужно |
|---|---|
| **`web-search-searxng`** | Docker Desktop запущен; контейнер сам поднимается через `docker-compose up` из папки скила |

Если Docker не установлен — `brew install --cask docker` (~5 мин на скачивание). Потом запусти `Docker.app` и подожди пока кит в трее загорится. Альтернатива — переключайся на `web-search-tavily` (с API ключом).

## System dependencies (через `brew install`)

Эти deps агент **сам ставит** при необходимости (правило «Local dev deps — install freely» в AGENTS.md), но если хочешь подготовить заранее:

```bash
brew install \
  graphviz \
  poppler \
  ghostscript \
  tesseract \
  imagemagick \
  pandoc \
  libreoffice
```

Что чему нужно:

| Скил | System deps |
|---|---|
| `diagram-generator` | `graphviz` (`dot`), `mmdc` (mermaid-cli, npm) |
| `document-analyzer` | `tesseract` (OCR), `poppler` (`pdftotext`/`pdfinfo`), `ghostscript` |
| `document-creator` | `node` + `docx` (npm), `libreoffice` (опц., для PDF-конверсии), python `python-docx`/`openpyxl`/`python-pptx` |
| `vision` | `imagemagick` (`convert`, `identify`) |
| `web-browser`, `webapp-testing` | Python + `playwright` + Chromium (`playwright install chromium`, ~375 MB RAM/session) |
| `code-runner` | Python deps из `skills/code-runner/requirements.txt` (pandas, numpy, matplotlib, …) |

## Без credentials и без Docker

Эти скилы работают сразу после `cp` без какой-либо настройки:

`api-tester`, `code-runner` (после `pip install -r requirements.txt`), `doc-coauthoring`, `find-skills` (опц. установит `skills.sh` CLI сам), `frontend-design`, `git-assistant` (нужен только `git` + `gh`), `mcp-builder`, `skill-creator`, `sql-toolkit` (нужен sqlite3/psql/mysql client под твою БД), `theme-factory`, `web-artifacts-builder`.

## Проверить что скил готов

```bash
openclaw skills list
```

Колонка `Status`: `✓ ready` — всё на месте; `△ needs setup` — что-то не хватает (system dep, env var, OAuth). Открой `skills/<name>/SKILL.md` чтобы понять, что именно.

## Безопасность

- `.env` в gitignore — не комить.
- Не выводи содержимое `.env` в чат / логи / коммиты.
- Если ключ скомпрометирован — сразу ротируй на стороне провайдера (Tavily/Maton/Google).
- macOS Keychain — более безопасная альтернатива для production: можно вытаскивать через `security find-generic-password` и подсасывать в env при старте сессии.
