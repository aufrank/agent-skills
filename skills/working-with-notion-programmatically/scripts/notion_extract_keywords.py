#!/usr/bin/env python3
"""Keyword/section extractor for Notion payload JSON files.

Searches page text for regex keywords and writes context snippets to markdown.
Deterministic and token-light; useful to locate relevant sections before opening
full payloads.
"""

import argparse
import json
import pathlib
import re
from typing import List, Pattern, Tuple


def compile_patterns(keywords: List[str], ignore_case: bool) -> List[Pattern[str]]:
    flags = re.IGNORECASE if ignore_case else 0
    return [re.compile(k, flags) for k in keywords]


def find_matches(lines: List[str], patterns: List[Pattern[str]], ctx: int) -> List[Tuple[int, int]]:
    """Return list of (start, end) line indices (inclusive) for matches with context."""
    spans: List[Tuple[int, int]] = []
    for idx, line in enumerate(lines):
        if any(p.search(line) for p in patterns):
            start = max(0, idx - ctx)
            end = min(len(lines) - 1, idx + ctx)
            spans.append((start, end))
    # merge overlapping spans
    merged: List[Tuple[int, int]] = []
    for start, end in spans:
        if not merged or start > merged[-1][1] + 1:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def format_snippet(lines: List[str], start: int, end: int) -> str:
    numbered = []
    width = len(str(end + 1))
    for i in range(start, end + 1):
        numbered.append(f"{str(i + 1).rjust(width)} | {lines[i].rstrip()}")
    return "\n".join(numbered)


def process_file(path: pathlib.Path, patterns: List[Pattern[str]], ctx: int) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    title = data.get("title", path.name)
    url = data.get("url", "")
    text = data.get("text", "")
    lines = text.splitlines()
    spans = find_matches(lines, patterns, ctx)
    parts: List[str] = []
    parts.append(f"# {title}")
    if url:
        parts.append(f"URL: {url}")
    if not spans:
        parts.append("(no matches)")
        return "\n\n".join(parts)
    for idx, (start, end) in enumerate(spans, 1):
        parts.append(f"## Match {idx} (lines {start + 1}-{end + 1})")
        parts.append("```text")
        parts.append(format_snippet(lines, start, end))
        parts.append("```")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract keyword contexts from Notion payloads.")
    parser.add_argument("--payload-dir", required=True, help="Directory with payload JSON files.")
    parser.add_argument("--output-dir", default="results/extracts", help="Directory for markdown outputs.")
    parser.add_argument("--keywords", nargs="+", required=True, help="Regex keywords to search for.")
    parser.add_argument("--context-lines", type=int, default=2, help="Number of context lines before/after match.")
    parser.add_argument("--ignore-case", action="store_true", help="Case-insensitive search.")
    args = parser.parse_args()

    payload_dir = pathlib.Path(args.payload_dir)
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    patterns = compile_patterns(args.keywords, args.ignore_case)

    for path in sorted(payload_dir.glob("*.json")):
        content = process_file(path, patterns, args.context_lines)
        out_path = output_dir / f"{path.stem}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
