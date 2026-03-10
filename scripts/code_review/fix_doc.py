"""Generate a fix document from review findings."""


def build_fix_doc(summary, findings):
    """Build a markdown document with fix instructions.

    Args:
        summary (str): The overall review summary.
        findings (list): List of Finding objects from
            the code review.

    Returns:
        str: Markdown document with actionable fix
            instructions for each finding.
    """
    lines = ["# Code Review — Fix Guide", ""]
    lines.append("## Summary")
    lines.append(summary)
    lines.append("")

    if not findings:
        lines.append("No issues found.")
        return "\n".join(lines)

    lines.append("## Findings")
    lines.append("")
    for i, f in enumerate(findings, 1):
        lines.append(
            f"### {i}. [{f.severity}/{f.category}]"
            f" `{f.file}:{f.line}`"
        )
        lines.append("")
        lines.append(f.comment)
        lines.append("")

    return "\n".join(lines)
