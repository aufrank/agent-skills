#!/usr/bin/env python3
"""Deterministic reducer for Notion payload JSON files.

Reads page payloads (from notion_fetch/notion_search_and_fetch) and emits
sectioned markdown summaries with truncated content to keep tokens low.
"""

import argparse
import json
import pathlib
import re
from typing import List, Tuple


def strip_prefix(text: str) -> str:
    """Drop boilerplate before the first heading if present."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith("#"):
            return "\n".join(lines[idx:])
    return text


def parse_sections(text: str) -> List[Tuple[str, List[str]]]:
    """Extract (heading, lines) pairs using markdown-style headings."""
    lines = text.splitlines()
    sections: List[Tuple[str, List[str]]] = []
    heading = None
    buf: List[str] = []
    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.*)", line)
        if match:
            if heading is not None:
                sections.append((heading, buf))
            heading = match.group(2).strip()
            buf = []
        else:
            buf.append(line.rstrip())
    if heading is not None:
        sections.append((heading, buf))
    return sections


def truncate_lines(lines: List[str], max_lines: int) -> List[str]:
    out = []
    for line in lines:
        if line.strip():
            out.append(line.strip())
        if len(out) >= max_lines:
            break
    return out


def summarize_payload(path: pathlib.Path, max_sections: int, max_lines: int) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    title = data.get("title", "")
    url = data.get("url", "")
    text = data.get("text", "")
    text = strip_prefix(text)
    sections = parse_sections(text)
    parts: List[str] = []
    parts.append(f"# {title or path.name}")
    if url:
        parts.append(f"URL: {url}")
    if not sections:
        parts.append("(No headings found)")
        return "\n\n".join(parts)
    for heading, lines in sections[:max_sections]:
        parts.append(f"## {heading}")
        snippet = truncate_lines(lines, max_lines)
        if snippet:
            parts.extend(snippet)
        else:
            parts.append("(empty section)")
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Notion payloads into compact markdown.")
    parser.add_argument("--payload-dir", required=True, help="Directory with payload JSON files.")
    parser.add_argument("--output-dir", default="results/summaries", help="Where to write markdown summaries.")
    parser.add_argument("--max-sections", type=int, default=30, help="Maximum sections to include per page.")
    parser.add_argument("--max-lines-per-section", type=int, default=8, help="Lines kept per section.")
    args = parser.parse_args()

    payload_dir = pathlib.Path(args.payload_dir)
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(payload_dir.glob("*.json")):
        summary = summarize_payload(path, args.max_sections, args.max_lines_per_section)
        out_path = output_dir / f"{path.stem}.md"
        out_path.write_text(summary, encoding="utf-8")
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
