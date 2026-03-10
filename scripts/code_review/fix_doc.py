"""Generate a fix document from review findings."""


def build_fix_doc(summary, findings):
    """Build a markdown fix guide with do/don't examples.

    Args:
        summary (str): The overall review summary.
        findings (list): List of Finding objects from
            the code review.

    Returns:
        str: Markdown document with actionable fix
            instructions and code examples.
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
        if f.dont:
            lines.append("**Don't:**")
            lines.append(f"```python\n{f.dont}\n```")
            lines.append("")
        if f.do:
            lines.append("**Do:**")
            lines.append(f"```python\n{f.do}\n```")
            lines.append("")

    return "\n".join(lines)
