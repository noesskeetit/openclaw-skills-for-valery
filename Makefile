.PHONY: build-all build-docs build-dev build-web build-viz test

build-all:
	docker compose --profile all build

build-docs:
	docker compose --profile docs build

build-dev:
	docker compose --profile dev build

build-web:
	docker compose --profile web build

build-viz:
	docker compose --profile viz build

test:
	@echo "=== document-analyzer ==="
	docker run --rm openclaw-skills-document-analyzer scripts/convert_pdf_to_images.py --help || true
	@echo "=== document-creator ==="
	docker run --rm openclaw-skills-document-creator scripts/recalc.py --help || true
	@echo "=== web-browser ==="
	docker run --rm openclaw-skills-web-browser scripts/browse.py --help || true
	@echo "=== code-runner ==="
	docker run --rm openclaw-skills-code-runner scripts/run_python.py --help || true
	@echo "=== diagram-generator ==="
	docker run --rm openclaw-skills-diagram-generator scripts/generate_mermaid.py --help || true
	@echo "All skills OK"
