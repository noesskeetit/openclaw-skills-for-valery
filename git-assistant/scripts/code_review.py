"""
Collect context for code review of the current branch.

Gathers the full diff and commit log between the current branch
and the base branch. The agent uses this context to produce
a structured review with categorized findings.

Usage:
    python3 code_review.py
    python3 code_review.py --base develop

Requires: git
"""

import argparse
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
            timeout=60,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error running git {' '.join(args)}: {e}", file=sys.stderr)
        return ""


def get_current_branch():
    """Get the name of the current branch."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def get_diff(base):
    """Get the full diff between base and HEAD."""
    return run_git(["diff", f"{base}...HEAD"])


def get_diff_stat(base):
    """Get a summary of changes between base and HEAD."""
    return run_git(["diff", "--stat", f"{base}...HEAD"])


def get_changed_files(base):
    """Get a list of changed files between base and HEAD."""
    output = run_git(["diff", "--name-only", f"{base}...HEAD"])
    return output.splitlines() if output else []


def get_commit_log(base):
    """Get commit log between base and HEAD."""
    return run_git(["log", "--oneline", f"{base}...HEAD"])


def get_commit_count(base):
    """Get the number of commits between base and HEAD."""
    output = run_git(["rev-list", "--count", f"{base}...HEAD"])
    try:
        return int(output)
    except ValueError:
        return 0


def check_base_exists(base):
    """Check if the base branch/ref exists."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", base],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Collect context for code review of the current branch."
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to compare against (default: main)",
    )
    args = parser.parse_args()

    if not check_base_exists(args.base):
        print(json.dumps({
            "error": f"Base branch '{args.base}' does not exist. "
                     f"Specify a valid branch with --base.",
        }, indent=2))
        sys.exit(1)

    current_branch = get_current_branch()

    if current_branch == args.base:
        print(json.dumps({
            "error": f"Currently on '{args.base}'. "
                     f"Switch to a feature branch before requesting a review.",
        }, indent=2))
        sys.exit(1)

    commit_count = get_commit_count(args.base)

    if commit_count == 0:
        print(json.dumps({
            "error": f"No commits found between '{args.base}' and '{current_branch}'.",
        }, indent=2))
        sys.exit(1)

    payload = {
        "current_branch": current_branch,
        "base_branch": args.base,
        "commit_count": commit_count,
        "commits": get_commit_log(args.base),
        "diff_stat": get_diff_stat(args.base),
        "changed_files": get_changed_files(args.base),
        "diff": get_diff(args.base),
        "instruction": (
            "Review the diff between the current branch and the base branch. "
            "Categorize findings as: "
            "[critical] for bugs, security issues, data loss risks; "
            "[suggestion] for improvements to logic, readability, performance; "
            "[nitpick] for style, naming, minor preferences. "
            "Reference specific file:line for each finding. "
            "Check for: unhandled errors, hardcoded secrets, missing tests, "
            "breaking API changes, and performance concerns."
        ),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
