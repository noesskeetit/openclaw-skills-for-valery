#!/usr/bin/env python3
"""Execute Python code in sandbox, capture output and generated files."""
import argparse
import subprocess
import sys
import os
import json
import glob


def main():
    parser = argparse.ArgumentParser(description='Run Python code in sandbox')
    parser.add_argument('script', help='Path to .py file or inline code (with -c)')
    parser.add_argument('-c', '--code', action='store_true',
                        help='Treat script arg as inline code')
    parser.add_argument('--timeout', type=int, default=60,
                        help='Timeout in seconds')
    args = parser.parse_args()

    workspace = os.environ.get('WORKSPACE', '/workspace')
    os.makedirs(workspace, exist_ok=True)
    before = set(glob.glob(f'{workspace}/**', recursive=True))

    cmd = [sys.executable, '-c', args.script] if args.code else [sys.executable, args.script]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            cwd=workspace,
        )
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout = ''
        stderr = f'Timeout after {args.timeout}s'

    after = set(glob.glob(f'{workspace}/**', recursive=True))
    new_files = sorted(after - before)

    print(json.dumps({
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "new_files": new_files,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
