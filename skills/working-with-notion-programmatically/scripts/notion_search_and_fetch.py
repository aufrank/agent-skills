#!/usr/bin/env python3
"""
Run a Notion search via mcpc, then bulk fetch matching pages in one shot.
Cuts down on multiple approvals by chaining search + fetch in a single script.
Also emits ID lists for downstream mention extraction and user resolution.
"""
from __future__ import annotations

import argparse
import json
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
from notion_bulk_fetch import (
    _extract_plain,
    _parse_payload,
    _run_fetch,
    _slugify,
    _trim,
)

def _parse_search_payload(data: Any) -> Optional[Dict[str, Any]]:
    """Extract the search payload from mcpc --json output."""
    if isinstance(data, dict) and "results" in data:
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


def _build_search_cmd(args: argparse.Namespace) -> List[str]:
    cmd: List[str] = [
        get_mcpc_bin(),
        "--json",
        "--profile",
        args.profile,
        args.session,
        "tools-call",
        "notion-search",
        f"query:={args.query}",
        f"query_type:={args.query_type}",
    ]
    if args.content_search_mode:
        cmd.append(f"content_search_mode:={args.content_search_mode}")
    if args.page_url:
        cmd.append(f"page_url:={args.page_url}")
    if args.data_source_url:
        cmd.append(f"data_source_url:={args.data_source_url}")
    if args.teamspace_id:
        cmd.append(f"teamspace_id:={args.teamspace_id}")
    if args.filters:
        cmd.append(f"filters:={args.filters}")
    if args.created_by:
        cmd.append(f"filters:={{\"created_by_user_ids\":[\"{args.created_by}\"]}}")
    return cmd


def _collect_targets(results: List[Dict[str, Any]], include_databases: bool) -> List[str]:
    targets: List[str] = []
    for entry in results:
        rtype = entry.get("type")
        if rtype != "page" and not include_databases:
            continue
        identifier = entry.get("url") or entry.get("id")
        if identifier:
            targets.append(identifier)
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Notion then bulk fetch matching pages.")
    parser.add_argument("--query", required=True, help="Search text.")
    parser.add_argument("--query-type", default="internal", choices=["internal", "user"], help="Search scope.")
    parser.add_argument("--content-search-mode", choices=["workspace_search", "ai_search"], help="Override Notion search mode.")
    parser.add_argument("--page-url", help="Restrict search to page/tree (URL or ID).")
    parser.add_argument("--data-source-url", help="Restrict search to a database data source (collection://...).")
    parser.add_argument("--teamspace-id", help="Restrict search to teamspace.")
    parser.add_argument("--filters", help="JSON object for filters (created_by_user_ids, created_date_range, etc.).")
    parser.add_argument("--created-by", help="Creator user ID (shorthand for filters.created_by_user_ids=[id]).")
    parser.add_argument("--include-databases", action="store_true", help="Also fetch database results (default: pages only).")
    parser.add_argument("--max-chars", type=int, default=800, help="Max characters per snippet (0 for full).")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL (quote @notion in PowerShell).")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile.")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server.")
    parser.add_argument("--search-output", default="results/search_and_fetch.search.json", help="Path to write raw search payload.")
    parser.add_argument("--search-ids-output", default="results/search_and_fetch.search_ids.txt", help="Path to write search result IDs/urls.")
    parser.add_argument("--output", default="results/search_and_fetch.fetch.json", help="Path to write aggregated fetch JSON.")
    parser.add_argument("--snippets-output", default="results/search_and_fetch.snippets.txt", help="Path to write snippets.")
    parser.add_argument("--fetch-ids-output", default="results/search_and_fetch.fetch_ids.txt", help="Path to write fetch target IDs/urls.")
    parser.add_argument("--payload-dir", help="Directory to write per-page payload JSON files.")
    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)

    search_cmd = _build_search_cmd(args)
    print("Executing search:", " ".join(search_cmd))
    search_proc = subprocess.run(
        search_cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if search_proc.returncode != 0:
        sys.stderr.write(f"Search failed with status {search_proc.returncode}\n{search_proc.stderr}\n")
        sys.exit(search_proc.returncode)

    try:
        search_data = json.loads(search_proc.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse search JSON: {exc}\n")
        sys.exit(1)

    search_payload = _parse_search_payload(search_data)
    if not search_payload:
        sys.stderr.write("Could not find search payload in response.\n")
        sys.exit(1)

    results = search_payload.get("results") or []
    write_json(resolve_path(args.search_output), search_payload)
    search_ids = [r.get("url") or r.get("id") or "" for r in results if (r.get("url") or r.get("id"))]
    write_text(resolve_path(args.search_ids_output), "\n".join(search_ids))
    if not results:
        print("No search results. Written search payload only.")
        sys.exit(0)

    targets = _collect_targets(results, args.include_databases)
    write_text(resolve_path(args.fetch_ids_output), "\n".join(targets))
    if not targets:
        print("Search results contained no fetchable targets (pages or databases).")
        sys.exit(0)

    mcpc_bin = get_mcpc_bin()
    payload_dir = resolve_path(args.payload_dir) if args.payload_dir else None
    if payload_dir:
        payload_dir.mkdir(parents=True, exist_ok=True)

    fetch_results: List[Dict[str, Any]] = []
    snippets: List[str] = []

    for target in targets:
        completed = _run_fetch(mcpc_bin, args.session, args.profile, target)
        if completed.returncode != 0:
            err = completed.stderr.strip() or f"mcpc returned {completed.returncode}"
            fetch_results.append({"id": target, "error": err})
            snippets.append(f"ID: {target}\nERROR: {err}\n")
            continue

        try:
            data = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            err = f"Failed to parse JSON: {exc}"
            fetch_results.append({"id": target, "error": err})
            snippets.append(f"ID: {target}\nERROR: {err}\n")
            continue

        payload = _parse_payload(data)
        if not payload:
            err = "Could not find payload in response"
            fetch_results.append({"id": target, "error": err})
            snippets.append(f"ID: {target}\nERROR: {err}\n")
            continue

        title = payload.get("title", "(untitled)")
        url = payload.get("url", "")
        content = payload.get("text", "")
        snippet_plain = _trim(_extract_plain(content), args.max_chars)
        entry = {
            "id": target,
            "title": title,
            "url": url,
            "length": len(content),
            "snippet": snippet_plain,
        }
        fetch_results.append(entry)
        snippets.append(f"Title: {title}\nURL: {url}\nLength: {len(content)} chars\n\n{snippet_plain}\n")

        if payload_dir:
            write_json(payload_dir / f"{_slugify(target)}.json", payload)

    write_json(resolve_path(args.output), {"results": fetch_results})
    write_text(resolve_path(args.snippets_output), "\n\n".join(snippets))
    print(f"Search payload saved to {args.search_output}")
    print(f"Search IDs saved to {args.search_ids_output}")
    print(f"Fetch IDs saved to {args.fetch_ids_output}")
    print(f"Fetch JSON saved to {args.output}")
    print(f"Snippets saved to {args.snippets_output}")


if __name__ == "__main__":
    main()