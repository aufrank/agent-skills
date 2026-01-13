#!/usr/bin/env python3
"""
Fetch a Notion page via mcpc and emit a compact summary (title, url, content snippet).
Writes snippet to a file to avoid dumping full Notion markdown.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any, Dict, Optional
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from notion_common import (
    DEFAULT_PROFILE,
    DEFAULT_SERVER,
    ensure_auth,
    get_mcpc_bin,
    write_json,
    write_text,
)


def _parse_payload(data: Any) -> Optional[Dict[str, Any]]:
    """Extract the nested JSON payload from mcpc --json output."""
    if isinstance(data, dict) and "text" in data:
        return data
    if isinstance(data, dict):
        content = data.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict):
                text = first.get("text")
                if isinstance(text, str):
                    try:
                        nested = json.loads(text)
                        if isinstance(nested, dict):
                            return nested
                    except json.JSONDecodeError:
                        return None
    return None


def _trim(s: str, max_chars: int) -> str:
    if max_chars <= 0:
        return s
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3] + "..."


def _extract_plain(text: str) -> str:
    """Very light cleanup of Notion markdown block dump for quick reading."""
    out = []
    in_tag = False
    for ch in text:
        if ch == "<":
            in_tag = True
            continue
        if ch == ">":
            in_tag = False
            continue
        if not in_tag:
            out.append(ch)
    return "".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch a Notion page and print a compact summary.")
    parser.add_argument("--id", required=True, help="Notion page URL/ID.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL. Quote @notion in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile to use (default: from MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server (default: https://mcp.notion.com/mcp).")
    parser.add_argument("--max-chars", type=int, default=800, help="Max characters of content to print (0 for full).")
    parser.add_argument("--output", default="results/fetch_snippet.txt", help="Path to write snippet text.")
    parser.add_argument("--payload-output", help="Optional path to write full JSON payload.")
    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)

    cmd = [
        get_mcpc_bin(),
        "--json",
        "--profile",
        args.profile,
        args.session,
        "tools-call",
        "notion-fetch",
        f"id:={args.id}",
    ]
    print("Executing:", " ".join(cmd))
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
        sys.stderr.write(completed.stderr)
        sys.exit(completed.returncode)

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
        sys.exit(1)

    payload = _parse_payload(data)
    if not payload:
        sys.stderr.write("Could not find a payload in the input.\n")
        sys.exit(1)

    title = payload.get("title", "(untitled)")
    url = payload.get("url", "")
    content = payload.get("text", "")
    snippet = _trim(_extract_plain(content), args.max_chars)

    summary = f"Title: {title}\nURL: {url}\nLength: {len(content)} chars\n\n{snippet}\n"
    print(summary)

    if args.output:
        write_text(Path(args.output), summary)
        print(f"Snippet saved to {args.output}")
    if args.payload_output:
        write_json(Path(args.payload_output), payload)
        print(f"Payload saved to {args.payload_output}")


if __name__ == "__main__":
    main()
