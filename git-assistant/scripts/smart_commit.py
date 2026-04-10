"""
Collect context for generating a smart commit message.

Gathers staged diff, working tree status, and recent commit history
into a single JSON payload. The agent uses this context to draft
a conventional commit message that matches the project's style.

Usage: python3 smart_commit.py

Requires: git
"""

import json
import subprocess
import sys


def run_git(args):
    """Run a git command and return its stdout. Returns empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error running git {' '.join(args)}: {e}", file=sys.stderr)
        return ""


def get_staged_diff():
    """Get the diff of staged changes."""
    return run_git(["diff", "--cached"])


def get_staged_stat():
    """Get a summary of staged changes (files and line counts)."""
    return run_git(["diff", "--cached", "--stat"])


def get_status():
    """Get the working tree status (short format)."""
    return run_git(["status", "--short"])


def get_recent_commits(count=5):
    """Get recent commit messages to match the project's style."""
    log = run_git(["log", "--oneline", f"-{count}"])
    return log.splitlines() if log else []


def get_staged_files():
    """Get a list of staged file paths."""
    output = run_git(["diff", "--cached", "--name-only"])
    return output.splitlines() if output else []


def main():
    staged_diff = get_staged_diff()

    if not staged_diff:
        print(json.dumps({
            "error": "No staged changes found. Stage files with 'git add' first.",
            "status": get_status(),
        }, indent=2))
        sys.exit(1)

    payload = {
        "staged_diff": staged_diff,
        "staged_stat": get_staged_stat(),
        "staged_files": get_staged_files(),
        "status": get_status(),
        "recent_commits": get_recent_commits(),
        "instruction": (
            "Analyze the staged diff and generate a commit message. "
            "Use conventional commit format (feat/fix/refactor/docs/test/chore). "
            "Focus on WHY the change was made, not just what changed. "
            "Match the style of recent commits when possible. "
            "Keep it to 1-2 sentences. "
            "Do NOT commit files containing secrets (.env, credentials, keys)."
        ),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
