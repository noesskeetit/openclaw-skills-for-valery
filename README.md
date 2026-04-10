# OpenClaw Skills

Набор скиллов для агента OpenClaw. Каждый скилл — самодостаточный модуль (Docker-образ или нативный скрипт) с универсальным форматом `SKILL.md`, совместимым с Claude Code, Cursor, Cline, Aider и OpenClaw.

Архитектура двухуровневая: **Core Tools** (файлы, bash, поиск, субагенты) встроены в рантайм агента, **Skills** — тяжёлые возможности в контейнерах.

## Состав

| Скилл | Назначение | Docker | Размер |
|-------|-----------|:------:|-------:|
| [code-runner](./code-runner) | Песочница Python 3.12 + Node.js 22 (pandas, numpy, matplotlib). Сеть отключена | Да | 1.36 GB |
| [diagram-generator](./diagram-generator) | Mermaid + Graphviz → SVG/PNG/PDF | Да | 2.53 GB |
| [document-analyzer](./document-analyzer) | Парсинг PDF/DOCX/XLSX/PPTX/CSV + OCR (pdfplumber, camelot, tesseract) | Да | 1.45 GB |
| [document-creator](./document-creator) | Создание DOCX/XLSX/PPTX/PDF (docx, pptxgenjs, openpyxl) | Да | 1.70 GB |
| [web-browser](./web-browser) | Playwright + Chromium: рендер JS, формы, скриншоты | Да | 2.01 GB |
| [web-search-searxng](./web-search-searxng) | Meta-поиск через self-hosted SearXNG. Без API-ключей, без лимитов | Да | ~0.20 GB |
| [web-search-tavily](./web-search-tavily) | AI-оптимизированный поиск через Tavily API (1000 req/month free) | Нет | — |
| [git-assistant](./git-assistant) | Коммиты, ревью изменений, PR-описания | Нет | — |

Итого Docker-образов: **~9.25 GB**.

## Формат скилла

Каждая папка содержит:

```
skill-name/
├── SKILL.md          # YAML frontmatter (name, description, license) + инструкции
├── scripts/          # исполняемые скрипты (Python, JS, shell)
├── Dockerfile        # для докеризованных скиллов
└── requirements.txt  # зависимости
```

`SKILL.md` описывает, **когда** использовать скилл и **как** вызывать его скрипты. Формат читается любым агентом, поддерживающим skills-протокол.

## Сборка

Через Makefile — профили из `docker-compose.yml`:

```bash
make build-all    # все скиллы
make build-docs   # document-analyzer + document-creator
make build-dev    # code-runner
make build-web    # web-browser + web-search
make build-viz    # diagram-generator
make test         # smoke-тесты --help по всем образам
```

Или напрямую:

```bash
docker compose --profile all build
```

## Запуск скилла вручную

```bash
# Пример: diagram-generator
mkdir -p /tmp/work && echo 'flowchart TD; A-->B' > /tmp/work/diagram.mmd
docker run --rm --entrypoint bash \
  -v /tmp/work:/work -w /work \
  openclaw-diagram-generator:latest \
  -c "python3 /skill/scripts/generate_mermaid.py diagram.mmd --output diagram.svg"
```

Код-раннер изолирован от сети (`network_mode: none`), остальные скиллы по умолчанию имеют доступ к интернету.

## Удалённый доступ

Для сценария «VM пользователя → Mac с Docker» есть тестовый HTTP gateway (`skill-gateway.py`, порт 5050, чистый Python stdlib, 11 REST-эндпоинтов) и SSH-обёртка (`skill-ssh-wrapper.sh`).

> **Важно:** `skill-gateway.py` — отдельный тестовый сервер, **не часть OpenClaw**. Для продакшена нужно выбрать способ интеграции: нативно в агенте, через MCP-сервер, или как внешний сервис.

## Статус

Все 8 скиллов протестированы локально и через HTTP gateway end-to-end (VM → tunnel → Mac → Docker). Детали в [`../docs/REPORT-skills-testing.md`](../docs/REPORT-skills-testing.md).

**Нюанс Apple Silicon:** образы собраны под `linux/amd64` и на M-чипах запускаются через Rosetta — работают, но с warning. Для Cloud.ru (Linux amd64) это несущественно.

## Лицензия

MIT (см. [LICENSE](./LICENSE)).
