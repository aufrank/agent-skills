#!/usr/bin/env python3
"""
Bulk fetch Notion pages via mcpc in one run.
- Takes multiple IDs/URLs from CLI or a newline-delimited file
- Writes aggregated snippets to a text file and structured data to JSON
- Also writes a newline-delimited ID list for downstream scripts
- Optional per-page payload dumps
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    resolve_path,
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
    """Light cleanup of Notion markdown to a flat snippet."""
    out: List[str] = []
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


def _slugify(identifier: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", identifier).strip("_") or "page"


def _run_fetch(mcpc_bin: str, session: str, profile: str, page_id: str) -> subprocess.CompletedProcess[str]:
    cmd = [
        mcpc_bin,
        "--json",
        "--profile",
        profile,
        session,
        "tools-call",
        "notion-fetch",
        f"id:={page_id}",
    ]
    print(f"Fetching {page_id}...")
    # Force UTF-8 decode to avoid cp1252 issues on Windows shells.
    return subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def _load_ids(args: argparse.Namespace) -> List[str]:
    ids: List[str] = []
    if args.ids_file:
        file_path = resolve_path(args.ids_file)
        ids.extend(
            line.strip()
            for line in file_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if args.ids:
        ids.extend(args.ids)
    # de-dupe preserving order
    seen = set()
    uniq: List[str] = []
    for value in ids:
        if value in seen:
            continue
        seen.add(value)
        uniq.append(value)
    return uniq


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk fetch Notion pages via mcpc with snippets and payloads.")
    parser.add_argument("--ids", nargs="*", help="Page URLs or IDs to fetch.")
    parser.add_argument("--ids-file", help="Path to newline-delimited list of page URLs/IDs.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL (quote @notion in PowerShell).")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile (default from MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server URL.")
    parser.add_argument("--max-chars", type=int, default=800, help="Max characters for each snippet (0 for full text).")
    parser.add_argument("--output", default="results/bulk_fetch.json", help="Path to write aggregated JSON.")
    parser.add_argument("--snippets-output", default="results/bulk_fetch_snippets.txt", help="Path to write text snippets.")
    parser.add_argument("--ids-output", default="results/bulk_fetch.ids.txt", help="Path to write newline-delimited IDs (urls).")
    parser.add_argument("--payload-dir", help="Directory to write per-page payload JSON files.")
    args = parser.parse_args()

    page_ids = _load_ids(args)
    if not page_ids:
        sys.stderr.write("No page IDs provided. Use --ids or --ids-file.\n")
        sys.exit(1)

    ensure_auth(args.server, args.profile, args.session)
    mcpc_bin = get_mcpc_bin()

    results: List[Dict[str, Any]] = []
    snippets: List[str] = []
    payload_dir = resolve_path(args.payload_dir) if args.payload_dir else None
    if payload_dir:
        payload_dir.mkdir(parents=True, exist_ok=True)

    for page_id in page_ids:
        completed = _run_fetch(mcpc_bin, args.session, args.profile, page_id)
        if completed.returncode != 0:
            err = completed.stderr.strip() or f"mcpc returned {completed.returncode}"
            results.append({"id": page_id, "error": err})
            snippets.append(f"ID: {page_id}\nERROR: {err}\n")
            continue

        try:
            data = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            err = f"Failed to parse JSON: {exc}"
            results.append({"id": page_id, "error": err})
            snippets.append(f"ID: {page_id}\nERROR: {err}\n")
            continue

        payload = _parse_payload(data)
        if not payload:
            err = "Could not find payload in response"
            results.append({"id": page_id, "error": err})
            snippets.append(f"ID: {page_id}\nERROR: {err}\n")
            continue

        title = payload.get("title", "(untitled)")
        url = payload.get("url", "")
        content = payload.get("text", "")
        snippet_plain = _trim(_extract_plain(content), args.max_chars)
        entry = {
            "id": page_id,
            "title": title,
            "url": url,
            "length": len(content),
            "snippet": snippet_plain,
        }
        results.append(entry)
        snippets.append(f"Title: {title}\nURL: {url}\nLength: {len(content)} chars\n\n{snippet_plain}\n")

        if payload_dir:
            safe_name = _slugify(page_id)
            write_json(payload_dir / f"{safe_name}.json", payload)

    write_json(resolve_path(args.output), {"results": results})
    write_text(resolve_path(args.snippets_output), "\n\n".join(snippets))
    write_text(resolve_path(args.ids_output), "\n".join(page_ids))
    print(f"Wrote JSON to {args.output}")
    print(f"Wrote snippets to {args.snippets_output}")
    print(f"Wrote ID list to {args.ids_output}")


if __name__ == "__main__":
    main()