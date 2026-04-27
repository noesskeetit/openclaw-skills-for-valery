#!/usr/bin/env python3
"""Convert SVG to PNG using cairosvg."""

import argparse
import os
import sys

try:
    import cairosvg
except ImportError:
    print(
        "Error: cairosvg is not installed. Run: pip install cairosvg",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert SVG to high-quality PNG.",
    )
    parser.add_argument(
        "input",
        help="Path to input SVG file.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output PNG file path. Defaults to input name with .png extension.",
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=None,
        help="Output width in pixels. Height scales proportionally unless also specified.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Output height in pixels. Width scales proportionally unless also specified.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(args.input)[1].lower()
    if ext != ".svg":
        print(f"Warning: input file does not have .svg extension: {args.input}", file=sys.stderr)

    output_path = args.output
    if output_path is None:
        output_path = os.path.splitext(args.input)[0] + ".png"

    kwargs: dict = {}
    if args.width is not None:
        kwargs["output_width"] = args.width
    if args.height is not None:
        kwargs["output_height"] = args.height

    try:
        cairosvg.svg2png(
            url=args.input,
            write_to=output_path,
            **kwargs,
        )
    except Exception as exc:
        print(f"Error converting SVG to PNG: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
