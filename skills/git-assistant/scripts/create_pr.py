"""
Collect context for creating a pull request.

Gathers branch info, diff stats, and full commit log so the agent
can generate a PR title and structured body with summary, changes,
and test plan sections.

Usage:
    python3 create_pr.py
    python3 create_pr.py --base develop

Requires: git, gh (GitHub CLI)
"""

import argparse
import json
import subprocess
import sys


def run_cmd(args, timeout=30):
    """Run a command and return its stdout. Returns empty string on failure."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error running {' '.join(args)}: {e}", file=sys.stderr)
        return ""


def run_git(args, timeout=30):
    """Run a git command and return its stdout."""
    return run_cmd(["git"] + args, timeout=timeout)


def get_current_branch():
    """Get the name of the current branch."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def get_remote_tracking_branch():
    """Get the remote tracking branch, if any."""
    return run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])


def has_unpushed_commits():
    """Check if there are commits not yet pushed to remote."""
    tracking = get_remote_tracking_branch()
    if not tracking:
        return True
    output = run_git(["rev-list", f"{tracking}..HEAD", "--count"])
    try:
        return int(output) > 0
    except ValueError:
        return True


def get_diff_stat(base):
    """Get a summary of changes between base and HEAD."""
    return run_git(["diff", "--stat", f"{base}...HEAD"])


def get_changed_files(base):
    """Get a list of changed files between base and HEAD."""
    output = run_git(["diff", "--name-only", f"{base}...HEAD"])
    return output.splitlines() if output else []


def get_commit_log(base):
    """Get commit log between base and HEAD with short hashes."""
    return run_git(["log", "--oneline", f"{base}...HEAD"])


COMMIT_SEPARATOR = "<<<COMMIT_BOUNDARY>>>"


def get_commit_messages(base):
    """Get full commit messages between base and HEAD.

    Commits are separated by COMMIT_SEPARATOR (a unique marker) so that
    commit bodies containing '---' (e.g. markdown separators, YAML
    frontmatter) are parsed correctly.
    """
    return run_git(["log", f"--format=%B{COMMIT_SEPARATOR}", f"{base}...HEAD"])


def get_commit_count(base):
    """Get the number of commits between base and HEAD."""
    output = run_git(["rev-list", "--count", f"{base}...HEAD"])
    try:
        return int(output)
    except ValueError:
        return 0


def get_diff(base):
    """Get the full diff between base and HEAD."""
    return run_git(["diff", f"{base}...HEAD"], timeout=60)


def check_base_exists(base):
    """Check if the base branch/ref exists."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", base],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def check_gh_available():
    """Check if GitHub CLI is available."""
    result = subprocess.run(
        ["gh", "--version"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Collect context for creating a pull request."
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch for the pull request (default: main)",
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
                     f"Switch to a feature branch before creating a PR.",
        }, indent=2))
        sys.exit(1)

    commit_count = get_commit_count(args.base)

    if commit_count == 0:
        print(json.dumps({
            "error": f"No commits found between '{args.base}' and '{current_branch}'.",
        }, indent=2))
        sys.exit(1)

    tracking_branch = get_remote_tracking_branch()
    needs_push = has_unpushed_commits()

    payload = {
        "current_branch": current_branch,
        "base_branch": args.base,
        "tracking_branch": tracking_branch or None,
        "needs_push": needs_push,
        "gh_available": check_gh_available(),
        "commit_count": commit_count,
        "commits": get_commit_log(args.base),
        "commit_messages": get_commit_messages(args.base),
        "commit_separator": COMMIT_SEPARATOR,
        "diff_stat": get_diff_stat(args.base),
        "changed_files": get_changed_files(args.base),
        "diff": get_diff(args.base),
        "instruction": (
            "Create a pull request for the current branch. "
            "Analyze ALL commits, not just the latest. "
            "Generate a title under 70 characters. "
            "Generate a body with sections: "
            "## Summary (1-3 bullet points), "
            "## Changes (significant changes grouped logically), "
            "## Test plan (checklist of what to test). "
            "If needs_push is true, push the branch first with 'git push -u origin <branch>'. "
            "Use 'gh pr create' to create the PR."
        ),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
