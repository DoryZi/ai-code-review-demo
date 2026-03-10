# AI Code Reviewer

An AI-powered code review agent that automatically reviews GitHub PRs using Claude Code CLI and posts inline comments with actionable findings.

## How It Works

When a PR is opened or updated against `main` or `dev`, a GitHub Action triggers a 6-step review pipeline:

```
PR opened/pushed
  |
  v
[1] Check if this commit was already reviewed (skip if yes)
  |
  v
[2] Get the diff (full PR diff on first review, latest commit only on follow-ups)
  |
  v
[3] Send the diff to Claude Code CLI for review
  |
  v
[4] Build a fix guide with do/don't code examples
  |
  v
[5] Post a review on the PR with inline comments per finding
  |
  v
[6] Done
```

### First review vs. follow-ups

- **First push** -- reviews the full PR diff, up to 15 findings.
- **Subsequent pushes** -- reviews only the latest commit diff, capped at 5 findings.
- **Already reviewed** -- if the current commit SHA already has a bot review, the run is skipped entirely.

## Project Structure

```
agent_tools/code_review/      # The AI code review agent
  __main__.py                  # CLI entry point & pipeline orchestration
  diff.py                     # Git diff retrieval (full PR or latest commit)
  reviewer.py                 # Invokes Claude Code CLI, parses JSON response
  prompt.py                   # Review prompt template sent to Claude
  models.py                   # Finding dataclass (file, line, severity, etc.)
  schema.py                   # JSON schema for structured output
  commenter.py                # Posts review + inline comments via GitHub API
  dismiss.py                  # Detects prior bot reviews, dedup logic
  fix_doc.py                  # Generates markdown fix guide from findings
  verify.py                   # Import smoke test for all modules
  local_review.py              # Run reviews on local changes (no PR needed)

.claude/skills/review/
  SKILL.md                     # /review slash command for Claude Code

.github/workflows/
  code-review.yml              # GitHub Action that triggers the pipeline

todo.py                        # Sample CLI app (review target)
db.py                          # SQLite database layer
infra/                         # Helm + Terraform configs
```

## The Review Agent (`agent_tools/code_review/`)

### `reviewer.py` -- The core

Supports two providers:

- **Claude** (default) -- shells out to `claude -p --output-format json --max-turns 5`. Claude Code CLI handles auth, context, and tool use natively.
- **OpenAI** -- calls the OpenAI API directly via the `openai` Python package with `response_format: json_object`. Set `OPENAI_API_KEY` in your environment.

Both providers use the same prompt and return the same structured JSON. Each finding includes file, line number, severity, category, a comment, and do/don't code examples.

### `prompt.py` -- What Claude sees

The prompt asks Claude to act as a senior code reviewer looking for bugs, security issues, performance problems, style violations, and missing error handling. It enforces a strict JSON output format.

### `diff.py` -- Getting the right diff

Two modes: `get_pr_diff(base_ref)` for the full PR diff against the base branch, and `get_latest_commit_diff()` for incremental reviews. Both exclude lock files, migrations, markdown, and `.github/` files.

### `commenter.py` -- Posting results

Uses the GitHub Pull Request Reviews API (`gh api`) to post a single review with inline comments attached to specific lines. Each comment shows severity, category, and do/don't code examples.

### `dismiss.py` -- Deduplication

Checks existing bot reviews to avoid duplicate reviews on the same commit and to determine whether this is a first or follow-up review.

### `fix_doc.py` -- Fix guide

Generates a markdown document summarizing all findings with actionable fix instructions, appended to the review body.

## `/review` — Claude Code Skill

If you're working in Claude Code, you can run a review at any time with the `/review` slash command. It supports two modes:

### Claude mode (default)

Claude reviews the code directly — no subprocess, no API key needed. It reads the diff, examines full file context, and reports findings inline.

```
/review                          # review all uncommitted changes
/review --staged                 # review only staged changes
/review --branch main            # review changes vs. main
/review db.py                    # review a specific file's changes
```

### OpenAI mode

Pass `--provider openai` to route the review through the OpenAI API instead. Requires `OPENAI_API_KEY` in your environment and `pip install openai`.

```
/review --provider openai                        # review with GPT-4o
/review --provider openai --model gpt-4o-mini    # use a cheaper model
/review --staged --provider openai               # combine with scope flags
/review --branch main --provider openai          # diff vs. main, review with OpenAI
```

Under the hood, the OpenAI path delegates to `python3 -m agent_tools.code_review.local_review` which makes the API call and returns the findings.

The skill is defined in `.claude/skills/review/SKILL.md`.

## Setup

1. Add `ANTHROPIC_API_KEY` as a GitHub Actions secret in your repo settings.
2. The workflow installs Claude Code CLI (`@anthropic-ai/claude-code`) automatically.
3. Open a PR -- the review runs on every push.

## Running locally (no PR needed)

Review your uncommitted changes directly from the terminal:

```bash
source venv/bin/activate

# Review all uncommitted changes
python -m agent_tools.code_review.local_review

# Review only staged changes
python -m agent_tools.code_review.local_review --staged

# Review changes vs. a branch
python -m agent_tools.code_review.local_review --branch main

# Include a markdown fix guide in the output
python -m agent_tools.code_review.local_review --fix-doc

# Use OpenAI instead of Claude
python -m agent_tools.code_review.local_review --provider openai

# Use a specific OpenAI model
python -m agent_tools.code_review.local_review --provider openai --model gpt-4o-mini
```

## Running on a PR

```bash
# Requires gh CLI authenticated + ANTHROPIC_API_KEY
python -m agent_tools.code_review \
  --pr-number 42 \
  --base-ref main

# Verify all modules import correctly
python -m agent_tools.code_review.verify
```

## The sample app

A minimal CLI todo app used as the review target:

```bash
python todo.py add Buy groceries
python todo.py list
python todo.py done 1
python todo.py delete 1
```
