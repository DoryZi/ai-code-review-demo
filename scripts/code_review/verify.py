"""Verify all code review modules import correctly.

This file exists to trigger a self-review of the
code review tool itself. Run with:
    python -m scripts.code_review.verify
"""

from scripts.code_review.diff import get_pr_diff, get_latest_commit_diff
from scripts.code_review.reviewer import run_review
from scripts.code_review.dismiss import already_reviewed, count_bot_reviews, delete_old_reviews
from scripts.code_review.commenter import post_review
from scripts.code_review.fix_doc import build_fix_doc
from scripts.code_review.models import Finding
from scripts.code_review.prompt import REVIEW_PROMPT
from scripts.code_review.schema import REVIEW_SCHEMA

ALL_EXPORTS = [
    ("get_pr_diff", get_pr_diff),
    ("get_latest_commit_diff", get_latest_commit_diff),
    ("run_review", run_review),
    ("already_reviewed", already_reviewed),
    ("count_bot_reviews", count_bot_reviews),
    ("delete_old_reviews", delete_old_reviews),
    ("post_review", post_review),
    ("build_fix_doc", build_fix_doc),
    ("Finding", Finding),
    ("REVIEW_PROMPT", REVIEW_PROMPT),
    ("REVIEW_SCHEMA", REVIEW_SCHEMA),
]

if __name__ == "__main__":
    for name, obj in ALL_EXPORTS:
        print(f"  OK: {name}")
    print(f"All {len(ALL_EXPORTS)} exports verified.")
