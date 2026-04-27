#!/usr/bin/env python3
"""Render Mermaid diagrams (.mmd) to SVG, PNG, or PDF via mermaid-cli (mmdc)."""

import argparse
import os
import subprocess
import sys
import tempfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate SVG/PNG/PDF from a Mermaid diagram.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to .mmd file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path. Format is inferred from extension (.svg, .png, .pdf).",
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=800,
        help="Output width in pixels (default: 800).",
    )
    parser.add_argument(
        "--theme", "-t",
        choices=["default", "dark", "forest", "neutral"],
        default="default",
        help="Mermaid theme (default: default).",
    )
    return parser.parse_args()


def resolve_input(input_path: str | None) -> str:
    """Return a path to the input .mmd file, creating a temp file from stdin if needed."""
    if input_path is not None:
        if not os.path.isfile(input_path):
            print(f"Error: input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        return input_path

    if sys.stdin.isatty():
        print("Error: no input file specified and nothing on stdin.", file=sys.stderr)
        sys.exit(1)

    content = sys.stdin.read()
    if not content.strip():
        print("Error: empty input from stdin.", file=sys.stderr)
        sys.exit(1)

    tmp = tempfile.NamedTemporaryFile(suffix=".mmd", delete=False, mode="w")
    tmp.write(content)
    tmp.close()
    return tmp.name


def detect_format(output_path: str) -> str:
    ext = os.path.splitext(output_path)[1].lower()
    fmt_map = {".svg": "svg", ".png": "png", ".pdf": "pdf"}
    fmt = fmt_map.get(ext)
    if fmt is None:
        print(
            f"Error: unsupported output format '{ext}'. Use .svg, .png, or .pdf.",
            file=sys.stderr,
        )
        sys.exit(1)
    return fmt


def get_puppeteer_config() -> str:
    """Create a temp puppeteer config with --no-sandbox for Docker environments."""
    import json
    config = {"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(config, tmp)
    tmp.close()
    return tmp.name


def run_mmdc(input_path: str, output_path: str, width: int, theme: str) -> None:
    fmt = detect_format(output_path)
    puppeteer_config = get_puppeteer_config()

    cmd = [
        "mmdc",
        "--input", input_path,
        "--output", output_path,
        "--width", str(width),
        "--theme", theme,
        "--puppeteerConfigFile", puppeteer_config,
    ]

    if fmt == "pdf":
        cmd.extend(["--pdfFit"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        os.unlink(puppeteer_config)
        print(
            "Error: 'mmdc' not found. Install mermaid-cli:\n"
            "  npm install -g @mermaid-js/mermaid-cli\n"
            "(requires Node.js; first install also downloads ~470 MB Chromium into ~/.cache/puppeteer)",
            file=sys.stderr,
        )
        sys.exit(1)

    os.unlink(puppeteer_config)

    if result.returncode != 0:
        stderr_lower = (result.stderr or "").lower()
        if "chromium" in stderr_lower or "puppeteer" in stderr_lower or "could not find browser" in stderr_lower:
            print(
                "Error: Chromium for Mermaid (puppeteer) is not available.\n"
                "Fix:\n"
                "  1. Run: npx puppeteer browsers install chrome\n"
                "  2. Or reinstall mermaid-cli: npm install -g @mermaid-js/mermaid-cli\n"
                "  3. Check corporate proxy / network if the download was blocked\n"
                "     (puppeteer downloads ~170 MB from storage.googleapis.com into ~/.cache/puppeteer)",
                file=sys.stderr,
            )
            if result.stderr:
                print("\n--- mmdc stderr ---", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

        print(f"mmdc failed (exit {result.returncode}):", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    print(f"Generated: {output_path}")


def main() -> None:
    args = parse_args()
    input_path = resolve_input(args.input)
    is_temp = args.input is None

    try:
        run_mmdc(input_path, args.output, args.width, args.theme)
    finally:
        if is_temp:
            os.unlink(input_path)


if __name__ == "__main__":
    main()
