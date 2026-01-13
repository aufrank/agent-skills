#!/usr/bin/env python3
"""
Resolve Notion user IDs to names/emails via notion-get-user.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from notion_common import (
    DEFAULT_PROFILE,
    DEFAULT_SERVER,
    ensure_auth,
    get_mcpc_bin,
    write_json,
    write_text,
    resolve_path,
)


def _normalize_id(uid: str) -> str:
    return uid.replace("user://", "") if uid.startswith("user://") else uid


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
    seen = set()
    uniq: List[str] = []
    for value in ids:
        norm = _normalize_id(value)
        if norm in seen:
            continue
        seen.add(norm)
        uniq.append(norm)
    return uniq


def _call_get_user(mcpc_bin: str, session: str, profile: str, user_id: str) -> Dict:
    payload = json.dumps({"path": {"user_id": user_id}})
    proc = subprocess.run(
        [mcpc_bin, "--json", "--profile", profile, session, "tools-call", "notion-get-user", payload],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"mcpc returned {proc.returncode}")
    try:
        outer = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse mcpc JSON: {exc}")
    content = outer.get("content")
    if not isinstance(content, list) or not content:
        raise RuntimeError("No content in response")
    first = content[0]
    text = first.get("text") if isinstance(first, dict) else None
    if not isinstance(text, str):
        raise RuntimeError("Missing text payload")
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve Notion user IDs to user objects.")
    parser.add_argument("--ids", nargs="*", help="User IDs to resolve.")
    parser.add_argument("--ids-file", help="Path to newline-delimited user IDs.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL (quote @notion in PowerShell).")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile.")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server.")
    parser.add_argument("--json-output", default="results/user_lookup.json", help="Path to write user objects.")
    parser.add_argument("--text-output", default="results/user_lookup.txt", help="Path to write name/email/id lines.")
    args = parser.parse_args()

    user_ids = _load_ids(args)
    if not user_ids:
        sys.stderr.write("No user IDs provided. Use --ids or --ids-file.\n")
        sys.exit(1)

    ensure_auth(args.server, args.profile, args.session)
    mcpc_bin = get_mcpc_bin()

    users: List[Dict] = []
    lines: List[str] = []
    for uid in user_ids:
        try:
            user = _call_get_user(mcpc_bin, args.session, args.profile, uid)
            users.append(user)
            name = user.get("name", "(unknown)")
            email = (user.get("person") or {}).get("email", "")
            lines.append(f"{name} | {email} | {uid}")
        except Exception as exc:  # pragma: no cover - defensive
            users.append({"id": uid, "error": str(exc)})
            lines.append(f"ERROR | {uid} | {exc}")

    json_path = resolve_path(args.json_output)
    text_path = resolve_path(args.text_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(json_path, {"users": users})
    write_text(text_path, "\n".join(lines))
    print(f"Wrote users to {args.json_output}")
    print(f"Wrote user lines to {args.text_output}")


if __name__ == "__main__":
    main()