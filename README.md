# AI Code Review Demo

Demo project showing how to run AI-powered code reviews on GitHub PRs using Claude and GitHub Actions.

## What's Inside

- **Simple CLI todo app** — Python + SQLite, no external deps
- **Infrastructure** — Helm chart and Terraform config
- **AI Code Review Action** — GitHub Action that reviews PRs with Claude and posts inline comments

## Quick Start

```bash
source venv/bin/activate
python todo.py add Buy groceries
python todo.py list
python todo.py done 1
python todo.py delete 1
```

## AI Code Review

On every PR to `main` or `dev`, the `code-review.yml` workflow:

1. Gets the PR diff
2. Sends it to Claude for review
3. Posts inline comments on the PR with findings

### Setup

Add `ANTHROPIC_API_KEY` as a GitHub Actions secret in your repo settings.
