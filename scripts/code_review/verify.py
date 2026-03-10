"""Verify all code review modules import correctly.

This file exists to trigger a self-review of the
code review tool itself. Run with:
    python -m scripts.code_review.verify
"""

from scripts.code_review.diff import get_pr_diff
from scripts.code_review.diff import get_latest_commit_diff
from scripts.code_review.reviewer import run_review
from scripts.code_review.dismiss import already_reviewed
from scripts.code_review.dismiss import count_bot_reviews
from scripts.code_review.dismiss import delete_old_reviews
from scripts.code_review.commenter import post_review
from scripts.code_review.fix_doc import build_fix_doc
from scripts.code_review.models import Finding
from scripts.code_review.prompt import REVIEW_PROMPT

ALL_MODULES = [
    get_pr_diff,
    get_latest_commit_diff,
    run_review,
    already_reviewed,
    count_bot_reviews,
    delete_old_reviews,
    post_review,
    build_fix_doc,
    Finding,
    REVIEW_PROMPT,
]

if __name__ == "__main__":
    for mod in ALL_MODULES:
        name = getattr(mod, "__name__", str(mod)[:40])
        print(f"  OK: {name}")
    print(f"All {len(ALL_MODULES)} modules verified.")
