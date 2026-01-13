#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_event(log_file: Path | None, event: str, **fields: object) -> None:
    record = {"ts": now_iso(), "event": event, **fields}
    line = json.dumps(record, sort_keys=True)
    print(line)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


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


def load_manifest(manifest_path: Path) -> dict[str, object]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove worktrees listed in a manifest.")
    parser.add_argument("--manifest", required=True, help="Manifest JSON path from create_worktrees.py.")
    parser.add_argument("--delete-branches", action="store_true", help="Delete branches created for worktrees.")
    parser.add_argument("--force", action="store_true", help="Force removal (git worktree remove -f).")
    parser.add_argument("--prune", action="store_true", help="Run git worktree prune at the end.")
    parser.add_argument("--log-file", help="Path to append JSONL log records.")
    args = parser.parse_args()

    root = repo_root()
    manifest_path = Path(args.manifest).expanduser()
    manifest = load_manifest(manifest_path)
    log_file = Path(args.log_file).expanduser() if args.log_file else root / "progress.log"

    tasks = manifest.get("tasks", [])
    failures: list[dict[str, str]] = []
    for task in tasks:
        path = Path(task["path"])
        branch = task.get("branch")
        cmd = ["worktree", "remove"]
        if args.force:
            cmd.append("-f")
        cmd.append(str(path))

        log_event(log_file, "worktree.remove.start", path=str(path), branch=branch or "")
        result = run_git(cmd, root)
        if result.returncode != 0:
            failures.append({"path": str(path), "error": result.stderr.strip() or "remove failed"})
            log_event(log_file, "worktree.remove.error", path=str(path), stderr=result.stderr.strip())
            continue

        log_event(log_file, "worktree.remove.ok", path=str(path))

        if args.delete_branches and branch:
            result = run_git(["branch", "-D", branch], root)
            if result.returncode != 0:
                failures.append({"branch": branch, "error": result.stderr.strip() or "branch delete failed"})
                log_event(log_file, "worktree.branch.delete.error", branch=branch, stderr=result.stderr.strip())
            else:
                log_event(log_file, "worktree.branch.delete.ok", branch=branch)

    if args.prune:
        result = run_git(["worktree", "prune"], root)
        if result.returncode != 0:
            failures.append({"prune": "failed", "error": result.stderr.strip() or "prune failed"})
            log_event(log_file, "worktree.prune.error", stderr=result.stderr.strip())
        else:
            log_event(log_file, "worktree.prune.ok")

    if failures:
        log_event(log_file, "worktree.cleanup.failed", failures=failures)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
