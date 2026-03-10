"""JSON schema for Claude structured output."""

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "Brief overall review summary.",
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "severity": {
                        "type": "string",
                        "enum": [
                            "critical", "warning",
                            "suggestion", "nitpick",
                        ],
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "bug", "security",
                            "performance", "style",
                            "testing", "logic",
                        ],
                    },
                    "comment": {"type": "string"},
                },
                "required": [
                    "file", "line", "severity",
                    "category", "comment",
                ],
            },
        },
    },
    "required": ["summary", "findings"],
}
