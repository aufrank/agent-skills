#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=False,
        text=True,
        capture_output=True,
    )


def repo_root() -> Path:
    result = run_git(["rev-parse", "--show-toplevel"], Path.cwd())
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to locate git repo root.")
    return Path(result.stdout.strip())


def parse_porcelain(output: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            if current:
                entries.append(current)
            current = {"path": value.strip()}
        else:
            current[key] = value.strip()
    if current:
        entries.append(current)
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Show git worktree status.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    root = repo_root()
    result = run_git(["worktree", "list", "--porcelain"], root)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "git worktree list failed")

    entries = parse_porcelain(result.stdout)
    if args.json:
        print(json.dumps(entries, indent=2))
        return

    for entry in entries:
        path = entry.get("path", "")
        branch = entry.get("branch", "(detached)")
        head = entry.get("HEAD", "")
        detached = "detached" if "detached" in entry else ""
        parts = [path, branch, head, detached]
        print(" | ".join(part for part in parts if part))


if __name__ == "__main__":
    main()
