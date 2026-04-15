# OpenClaw Skills

A set of agent-agnostic skills for coding agents (OpenClaw, Claude Code, Cursor, Cline, Aider, etc.). Each skill is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) and a `scripts/` directory of executables the agent can call.

No Docker images, no gateway service, no external runtime — just markdown + scripts. The host environment is responsible for installing dependencies and providing isolation.

## Skills

| Skill | Purpose | Heavy deps |
|---|---|---|
| [code-runner](./code-runner) | Execute Python or JavaScript with stdout/stderr/file capture | pandas, numpy, matplotlib (~420 MB venv) |
| [diagram-generator](./diagram-generator) | Mermaid + Graphviz → SVG/PNG/PDF | graphviz binary, mermaid-cli (~470 MB Chromium cache) |
| [document-analyzer](./document-analyzer) | Read/extract/OCR PDF, DOCX, XLSX, PPTX, CSV; PDF form filling | tesseract, poppler, ghostscript |
| [document-creator](./document-creator) | Create and validate DOCX, XLSX, PPTX, PDF; OOXML schema validation | python-docx, openpyxl, pptx, reportlab, OOXML XSD schemas (bundled) |
| [git-assistant](./git-assistant) | Commits, code review, PR descriptions | stdlib only |
| [web-browser](./web-browser) | Browser automation: navigate, screenshot, fill forms via Playwright | playwright + Chromium (~525 MB) |
| [web-search-searxng](./web-search-searxng) | Meta-search via self-hosted SearXNG (auto-bootstraps its container) | docker daemon access |
| [web-search-tavily](./web-search-tavily) | AI-optimized search via Tavily API | stdlib only, requires `TAVILY_API_KEY` |

## Skill format

```
skill-name/
├── SKILL.md           # YAML frontmatter + instructions for the agent
├── requirements.txt   # Python deps (when applicable)
└── scripts/           # executables the agent invokes
```

`SKILL.md` starts with a YAML block:

```yaml
---
name: skill-name
description: "When to use this skill, what it does, what it does NOT do."
license: MIT
---
```

The `description` is what the agent reads to decide when to invoke the skill. The body explains how to use the scripts.

## Install a single skill

```bash
cd skill-name
pip install -r requirements.txt   # if present
# install any system deps listed in SKILL.md (tesseract, graphviz, ...)
```

For skills that ship their own service (currently only `web-search-searxng`), the script auto-starts the container on first call — no manual setup needed beyond a working docker daemon.

## Resource footprint

Designed to coexist on a small VM (≥2 GB RAM, ~10 GB disk). Heaviest skills:

- **web-browser** — peak ~375 MB RAM per Chromium session
- **diagram-generator** — peak ~500 MB-1 GB during Mermaid render
- **document-analyzer** — up to ~1 GB on large PDFs with OCR
- **web-search-searxng** — ~200-300 MB resident as background container

Run heavy skills serially on constrained hardware.

## Adding a new skill

1. Create `your-skill/` with `SKILL.md` and `scripts/`
2. Use the YAML frontmatter format above
3. Make `description` tell the agent **when** and **when NOT** to use the skill
4. Document each script's CLI in `SKILL.md`
5. Pin major versions in `requirements.txt` if Python deps are involved

## License

MIT — see [LICENSE](./LICENSE).
