from __future__ import annotations

import re
from collections import defaultdict

_HEADING_PATTERN = re.compile(r"^(#{1,6}\s+.+|[A-Z][A-Za-z0-9\s]{2,}:)$")


def estimate_tokens(text: str) -> int:
    # rough estimate: 1 token ~= 4 chars
    return max(1, len(text) // 4)


def extract_topics(text: str) -> dict[str, list[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return {"General": []}

    topic = "General"
    sections: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        if _HEADING_PATTERN.match(line):
            topic = line.lstrip("#").strip().rstrip(":")
            continue
        sections[topic].append(line)
    return dict(sections)
