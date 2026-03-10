"""Run a code review on local changes without a PR.

Usage:
    python -m agent_tools.code_review.local_review
    python -m agent_tools.code_review.local_review --staged
    python -m agent_tools.code_review.local_review --branch main
    python -m agent_tools.code_review.local_review --provider openai
    python -m agent_tools.code_review.local_review --provider openai --model gpt-5.4
"""

import argparse
import subprocess
import sys

from agent_tools.code_review.reviewer import run_review
from agent_tools.code_review.fix_doc import build_fix_doc

MAX_DIFF_CHARS = 100_000

SEV_COLORS = {
    "critical": "\033[91m",
    "warning": "\033[93m",
    "suggestion": "\033[96m",
    "nitpick": "\033[90m",
}
RESET = "\033[0m"


def _get_diff(staged_only, branch):
    """Get local git diff.

    Args:
        staged_only (bool): If True, review only staged
            changes. If False, review all uncommitted.
        branch (str): If set, diff against this branch
            instead of uncommitted changes.

    Returns:
        str: The unified diff output.

    Raises:
        subprocess.CalledProcessError: If git fails.
    """
    if branch:
        cmd = ["git", "diff", f"{branch}...HEAD"]
    elif staged_only:
        cmd = ["git", "diff", "--cached"]
    else:
        cmd = ["git", "diff", "HEAD"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True,
    )
    return result.stdout


def _print_findings(summary, findings):
    """Print findings to terminal with color.

    Args:
        summary (str): Review summary text.
        findings (list): List of Finding objects.

    Returns:
        None.
    """
    print(f"\n{'='*60}")
    print("AI CODE REVIEW")
    print(f"{'='*60}\n")
    print(summary)
    print()
    if not findings:
        print("No issues found.")
        return
    print(f"{len(findings)} finding(s):\n")
    for i, finding in enumerate(findings, 1):
        color = SEV_COLORS.get(finding.severity, "")
        print(
            f"{color}{i}. [{finding.severity}/{finding.category}]"
            f" {finding.file}:{finding.line}{RESET}"
        )
        print(f"   {finding.comment}\n")


def main():
    """Run local code review on uncommitted changes.

    Returns:
        None.

    Raises:
        SystemExit: On empty diff or arg errors.
    """
    parser = argparse.ArgumentParser(
        description="Review local changes with AI",
    )
    parser.add_argument(
        "--staged", action="store_true",
        help="Review only staged changes",
    )
    parser.add_argument(
        "--branch", type=str, default="",
        help="Diff against a branch (e.g. main)",
    )
    parser.add_argument(
        "--fix-doc", action="store_true",
        help="Print a markdown fix guide",
    )
    parser.add_argument(
        "--provider", type=str, default="claude",
        choices=["claude", "openai"],
        help="LLM provider (default: claude)",
    )
    parser.add_argument(
        "--model", type=str, default="",
        help="Model override (openai only)",
    )
    args = parser.parse_args()

    print("[1/3] Getting diff...")
    diff = _get_diff(args.staged, args.branch)
    if not diff.strip():
        print("No changes to review.")
        sys.exit(0)
    print(f"[1/3] Diff size: {len(diff)} chars")
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS]
        print("[1/3] Truncated to 100K chars.")

    provider = args.provider
    print(f"[2/3] Sending to {provider} for review...")
    summary, findings, cost = run_review(
        diff, provider=provider, model=args.model,
    )
    print(f"[2/3] Got {len(findings)} finding(s).")
    if cost.cost_usd > 0:
        print(f"[2/3] Cost: {cost}")

    print("[3/3] Results:")
    _print_findings(summary, findings)

    if args.fix_doc and findings:
        print(f"\n{'='*60}")
        print(build_fix_doc(summary, findings))


if __name__ == "__main__":
    main()
