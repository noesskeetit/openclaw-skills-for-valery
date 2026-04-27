#!/usr/bin/env python3
"""Execute JavaScript/Node.js code in sandbox, capture output and generated files."""
import argparse
import shutil
import subprocess
import os
import json
import glob


def main():
    parser = argparse.ArgumentParser(description='Run Node.js code in sandbox')
    parser.add_argument('script', help='Path to .js file or inline code (with -c)')
    parser.add_argument('-c', '--code', action='store_true',
                        help='Treat script arg as inline code')
    parser.add_argument('--timeout', type=int, default=60,
                        help='Timeout in seconds')
    args = parser.parse_args()

    node_bin = shutil.which('node')
    if node_bin is None:
        print(json.dumps({
            "stdout": "",
            "stderr": "node executable not found in PATH",
            "exit_code": 127,
            "new_files": [],
        }, ensure_ascii=False, indent=2))
        return

    workspace = os.environ.get('WORKSPACE', '/workspace')
    os.makedirs(workspace, exist_ok=True)
    before = set(glob.glob(f'{workspace}/**', recursive=True))

    cmd = [node_bin, '-e', args.script] if args.code else [node_bin, args.script]
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
    new_files = sorted(p for p in (after - before) if os.path.isfile(p))

    print(json.dumps({
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "new_files": new_files,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
