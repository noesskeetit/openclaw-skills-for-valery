#!/usr/bin/env python3
"""Render Graphviz DOT files to SVG, PNG, or PDF."""

import argparse
import os
import subprocess
import sys
import tempfile


LAYOUT_ENGINES = ("dot", "neato", "fdp", "circo", "twopi", "sfdp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate SVG/PNG/PDF from a Graphviz DOT file.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to .dot file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path. Format is inferred from extension (.svg, .png, .pdf).",
    )
    parser.add_argument(
        "--layout", "-l",
        choices=LAYOUT_ENGINES,
        default="dot",
        help="Layout engine (default: dot).",
    )
    return parser.parse_args()


def resolve_input(input_path: str | None) -> str:
    """Return a path to the input .dot file, creating a temp file from stdin if needed."""
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

    tmp = tempfile.NamedTemporaryFile(suffix=".dot", delete=False, mode="w")
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


def run_graphviz(input_path: str, output_path: str, layout: str) -> None:
    fmt = detect_format(output_path)

    cmd = [
        layout,
        f"-T{fmt}",
        "-o", output_path,
        input_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print(
            f"Error: '{layout}' not found. Install Graphviz: apt-get install graphviz",
            file=sys.stderr,
        )
        sys.exit(1)

    if result.returncode != 0:
        print(f"{layout} failed (exit {result.returncode}):", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    print(f"Generated: {output_path}")


def main() -> None:
    args = parse_args()
    input_path = resolve_input(args.input)
    is_temp = args.input is None

    try:
        run_graphviz(input_path, args.output, args.layout)
    finally:
        if is_temp:
            os.unlink(input_path)


if __name__ == "__main__":
    main()
