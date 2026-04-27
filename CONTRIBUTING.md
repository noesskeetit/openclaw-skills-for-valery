# Contributing

Спасибо за желание расширить пресет. Короткий гайд ниже.

## Adding a new skill

### Что должно быть в `skills/your-skill/`

Минимум:

```
skills/your-skill/
└── SKILL.md
```

Расширенно (если есть код):

```
skills/your-skill/
├── SKILL.md             # YAML frontmatter + инструкции для агента (обязательно)
├── requirements.txt     # Python deps, если есть
├── package.json         # Node deps, если есть
├── scripts/             # Исполняемые скрипты, которые агент вызывает
│   └── do_something.py
└── references/          # Дополнительная документация
```

### `SKILL.md` frontmatter

```yaml
---
name: your-skill
description: "Concrete description of what this skill does, when to use it, and explicitly when NOT to use it. The agent reads this string to decide whether to invoke the skill — make it disambiguating."
license: MIT
---
```

Дальше тело markdown'а: как использовать скрипты, какие ожидаются inputs / outputs, какие deps.

### Хорошие `description` строки

- Первое предложение — что делает (action verb).
- Второе — когда использовать (триггер-фразы).
- Третье — когда НЕ использовать (граница со смежными скилами).

Пример из [`document-creator`](./skills/document-creator/SKILL.md):

> Use this skill when the user wants to create, edit, or manipulate office documents and PDFs — Word (.docx), Excel (.xlsx, .xlsm, .csv), PowerPoint (.pptx), PDF. Triggers: any mention of documents, spreadsheets, presentations… Do NOT use for Google Docs/Sheets or general coding tasks unrelated to document generation.

### Если скил требует credentials

1. Добавь нужный env var / OAuth path в [`workspace/.env.example`](./workspace/.env.example) с placeholder'ом и комментарием.
2. Допиши секцию в [`SECRETS.md`](./SECRETS.md) — где взять, как настроить.
3. (Опционально) если ключ часто блокирует — добавь skill name в example'ы «Missing deps or keys» секции [`workspace/AGENTS.md`](./workspace/AGENTS.md).

### Если скил требует system deps

`brew install <pkg>` / `pip install <pkg>` — агент **сам ставит** через правило «Local dev deps — install freely» в `AGENTS.md`. Дополнительная конфигурация в `AGENTS.md` обычно не нужна, но обнови соответствующую таблицу в `SECRETS.md` чтобы коллеги могли пред-установить если хотят.

### Категория в README

После того как скил готов, добавь его в одну из use-case категорий в [`README.md`](./README.md):

- 🧑‍💻 Для разработки
- 📊 Для анализа и работы с документами
- 🔍 Для исследований
- 🎨 Для дизайна и контента
- 🖼️ Для медиа
- 🧪 Для тестирования
- 🧭 Для самопрокачки агента

Если ни одна категория не подходит — заведи новую с эмодзи и описанием.

## PR flow

1. Форк → ветка `feat/your-skill` от `universal-agent` (default branch)
2. Коммиты — conventional (`feat: ...`, `fix: ...`, `chore: ...`)
3. PR в `universal-agent`, описание по шаблону:

   ```
   ## What it does
   ## When to use
   ## When NOT to use
   ## Setup required
   ## Smoke test result (paste output)
   ```

4. Перед PR — прогони smoke test реально:
   ```bash
   cp -R skills/your-skill ~/.openclaw/workspace/skills/
   openclaw gateway restart
   openclaw skills list  # должен показать your-skill ready или needs-setup
   openclaw agent --session-id smoke-yours --message "<типичная задача для скила>"
   ```

   В PR приложи финальный summary агента + скриншот / путь к артефактам.

## Bootstrap-файлы (`AGENTS.md`, `SOUL.md`)

Менять можно, но осторожно — это рельсы для всех 19 скилов. Перед PR:

- Запусти `e2e-1` (research pipeline), `e2e-2` (data ETL), `e2e-3` (build → test → ship) — все три должны пройти без падения в shell-fallback. См. test plan в первом merge-commit ([`a4529e3`](../../commit/a4529e3)).
- Запусти `e2e-stress` (~100 tool calls, autonomous task) — agent должен дойти до финала, todo.md актуален, WRONG_TURN'ы залогированы.

Без этих прогонов — изменения в `AGENTS.md` / `SOUL.md` не мерджим.

## Removing a skill

Если нужно вычистить скил из пресета:

1. `git rm -r skills/<name>`
2. Чистка упоминаний в:
   - `README.md` (категория, credits)
   - `SECRETS.md` (если был в credentials/Docker таблице)
   - `workspace/AGENTS.md` (Skills environment block, Missing deps примеры)
   - `workspace/TOOLS.md`
   - `workspace/.env.example`
3. PR → `universal-agent`, в описании — почему вычеркнули.

## Style

- README / SECRETS / CHANGELOG — русский (с английским там, где термины устоялись: Skills Protocol, Long-Task Workflow, etc.).
- `workspace/AGENTS.md`, `workspace/SOUL.md` — двуязычно: английский для имён секций и наследованных от OpenClaw template'ов, русский для комментариев и доп. правил.
- Conventional commits: `feat: ...` (новый скил / фича), `fix: ...` (баг), `chore: ...` (cleanup), `docs: ...` (только README/SECRETS).
