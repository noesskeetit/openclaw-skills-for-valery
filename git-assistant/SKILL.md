---
name: git-assistant
description: "Use this skill for git workflows: creating commits with meaningful messages, reviewing code changes, and creating pull requests. Analyzes staged/unstaged changes, follows conventional commit format, generates PR descriptions with summaries and test plans."
license: MIT
---

# Git Assistant Skill

Automates git workflows: crafting commit messages, reviewing diffs, and creating pull requests. Runs natively in the user's environment — no Docker or external services required. Only needs `git`, `gh` (for PRs), and Python 3.

## /commit workflow

Create a well-structured commit from staged changes.

### Steps

1. Run `git status` to see untracked and modified files (never use `-uall` flag)
2. Run `git diff --cached` to see staged changes that will be committed
3. Run `git log --oneline -5` to see recent commit message style in the repo
4. Analyze the nature of the changes — determine the type:
   - `feat` — new feature
   - `fix` — bug fix
   - `refactor` — code restructuring without behavior change
   - `docs` — documentation only
   - `test` — adding or updating tests
   - `chore` — tooling, config, dependencies
5. Draft a concise commit message (1-2 sentences):
   - Focus on **why** the change was made, not what files were touched
   - Follow conventional commit format: `type: description`
   - Match the style of recent commits in the repo when possible
6. Stage relevant files — prefer naming specific files over `git add -A` or `git add .`
7. **Never commit** files that may contain secrets: `.env`, `credentials.json`, API keys, tokens
8. Create the commit using HEREDOC for proper message formatting:

```bash
git commit -m "$(cat <<'EOF'
feat: add retry logic for transient API failures

Requests to the payment gateway occasionally timeout under load.
Adding exponential backoff prevents cascading failures downstream.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Using the script

```bash
python3 scripts/smart_commit.py
```

Collects diff, status, and recent commits into a single JSON payload for the agent to analyze and generate the commit message.

## /review workflow

Review code changes between branches with structured feedback.

### Steps

1. Determine the base branch (default: `main`)
2. Run `git diff <base>...HEAD` for the full diff of the current branch
3. Run `git log --oneline <base>...HEAD` for the commit history
4. Review the diff and categorize findings:
   - **[critical]** — bugs, security issues, data loss risks. Must be fixed before merge.
   - **[suggestion]** — improvements to logic, readability, performance. Should be considered.
   - **[nitpick]** — style, naming, minor preferences. Optional to address.
5. Reference specific locations as `file:line` for each finding
6. Check for:
   - Unhandled error paths or missing validation
   - Hardcoded secrets or credentials in the diff
   - Missing tests for new logic
   - Breaking changes to public APIs
   - Performance concerns (N+1 queries, unbounded loops, large allocations)

### Output format

```
## Code Review: feature/add-payments → main

### Critical
- **payments/handler.py:42** — `amount` is not validated before passing to the gateway.
  User input could be negative or zero, causing silent charge failures.

### Suggestions
- **payments/handler.py:58** — Consider extracting retry logic into a shared utility.
  The same pattern appears in `notifications/sender.py:31`.

### Nitpicks
- **payments/handler.py:12** — Unused import `datetime` can be removed.

### Summary
3 findings: 1 critical, 1 suggestion, 1 nitpick.
The payment validation gap should be addressed before merging.
```

### Using the script

```bash
python3 scripts/code_review.py
python3 scripts/code_review.py --base develop
```

Collects the full diff and commit log between the current branch and the base branch.

## /pr workflow

Create a pull request with a generated title and structured body.

### Steps

1. Check if the current branch tracks a remote and is pushed up to date
2. Push to remote with `-u` flag if needed
3. Analyze **all** commits on the branch (not just the latest) via `git log <base>...HEAD`
4. Analyze the full diff via `git diff <base>...HEAD`
5. Generate PR title — under 70 characters, concise
6. Generate PR body with structured sections:

```markdown
## Summary
- <1-3 bullet points describing the change>

## Changes
- <list of significant changes grouped logically>

## Test plan
- [ ] <what to test and how>
```

7. Create the PR:

```bash
gh pr create --title "the pr title" --body "$(cat <<'EOF'
## Summary
...

## Changes
...

## Test plan
...
EOF
)"
```

### Using the script

```bash
python3 scripts/create_pr.py
python3 scripts/create_pr.py --base develop
```

Collects branch info, diff stats, and commit log for the agent to generate the PR content.

## Scripts Reference

| Script | Purpose | Key args |
|---|---|---|
| `scripts/smart_commit.py` | Collect staged diff, status, recent commits | (none) |
| `scripts/code_review.py` | Collect branch diff and commits for review | `--base <branch>` |
| `scripts/create_pr.py` | Collect branch context for PR creation | `--base <branch>` |

All scripts output JSON to stdout. No external dependencies beyond `git` and Python 3 stdlib.
