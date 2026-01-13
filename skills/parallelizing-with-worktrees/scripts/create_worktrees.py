#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class TaskSpec:
    name: str
    branch: str | None
    slug: str


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


def current_branch(root: Path) -> str:
    result = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to read current branch.")
    return result.stdout.strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    if not slug:
        raise ValueError(f"Invalid task name: {value!r}")
    return slug


def parse_task_line(line: str, mode: str) -> TaskSpec | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if ":" in stripped:
        name_part, branch_part = (chunk.strip() for chunk in stripped.split(":", 1))
        name = name_part or branch_part
        branch = branch_part or None
    else:
        name = stripped
        branch = None
    if mode == "existing":
        branch = name if branch is None else branch
    return TaskSpec(name=name, branch=branch, slug=slugify(name))


def load_tasks(task_lines: Iterable[str], mode: str) -> list[TaskSpec]:
    tasks = []
    for line in task_lines:
        parsed = parse_task_line(line, mode)
        if parsed:
            tasks.append(parsed)
    if not tasks:
        raise ValueError("No tasks provided.")
    return tasks


def build_worktree_cmd(
    mode: str,
    base_branch: str,
    branch_name: str | None,
    path: Path,
) -> list[str]:
    if mode == "detach":
        return ["worktree", "add", "--detach", str(path), base_branch]
    if mode == "existing":
        if not branch_name:
            raise ValueError("Missing branch for existing mode.")
        return ["worktree", "add", str(path), branch_name]
    if not branch_name:
        raise ValueError("Missing branch for branch mode.")
    return ["worktree", "add", "-b", branch_name, str(path), base_branch]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create git worktrees for parallel tasks.")
    parser.add_argument("--tasks-file", help="Path to task list (one per line).")
    parser.add_argument("--task", action="append", help="Inline task (repeatable).")
    parser.add_argument("--mode", choices=["branch", "existing", "detach"], default="branch")
    parser.add_argument("--base-branch", help="Branch/commit to base new worktrees on.")
    parser.add_argument("--branch-prefix", help="Prefix for new branches (branch mode only).")
    parser.add_argument("--run-id", help="Run identifier for the output directory.")
    parser.add_argument("--root-dir", help="Root directory for worktrees.")
    parser.add_argument("--manifest-out", help="Path to write manifest.json.")
    parser.add_argument("--log-file", help="Path to append JSONL log records.")
    args = parser.parse_args()

    root = repo_root()
    base_branch = args.base_branch or current_branch(root)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    repo_name = root.name
    default_root = root.parent / f"{repo_name}-worktrees"
    root_dir = Path(args.root_dir).expanduser() if args.root_dir else default_root
    run_dir = root_dir / run_id

    manifest_path = Path(args.manifest_out).expanduser() if args.manifest_out else run_dir / "manifest.json"
    log_file = Path(args.log_file).expanduser() if args.log_file else root / "progress.log"

    task_lines: list[str] = []
    if args.tasks_file:
        task_lines.extend(Path(args.tasks_file).read_text(encoding="utf-8").splitlines())
    if args.task:
        task_lines.extend(args.task)
    tasks = load_tasks(task_lines, args.mode)

    branch_prefix = args.branch_prefix or run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "run_id": run_id,
        "repo_root": str(root),
        "base_branch": base_branch,
        "mode": args.mode,
        "worktree_root": str(run_dir),
        "tasks": [],
    }

    failures: list[dict[str, str]] = []
    for spec in tasks:
        branch_name = None
        if args.mode == "branch":
            branch_name = spec.branch or f"{branch_prefix}-{spec.slug}"
        elif args.mode == "existing":
            branch_name = spec.branch or spec.name

        worktree_path = run_dir / spec.slug
        if worktree_path.exists():
            failures.append({"task": spec.name, "error": "worktree path already exists"})
            continue

        cmd = build_worktree_cmd(args.mode, base_branch, branch_name, worktree_path)
        log_event(log_file, "worktree.create.start", task=spec.name, branch=branch_name, path=str(worktree_path))
        result = run_git(cmd, root)
        if result.returncode != 0:
            failures.append(
                {
                    "task": spec.name,
                    "branch": branch_name or "",
                    "error": result.stderr.strip() or "git worktree add failed",
                }
            )
            log_event(
                log_file,
                "worktree.create.error",
                task=spec.name,
                branch=branch_name,
                stderr=result.stderr.strip(),
            )
            continue

        manifest["tasks"].append(
            {
                "task": spec.name,
                "slug": spec.slug,
                "branch": branch_name,
                "path": str(worktree_path),
            }
        )
        log_event(log_file, "worktree.create.ok", task=spec.name, branch=branch_name, path=str(worktree_path))

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log_event(log_file, "worktree.manifest.written", path=str(manifest_path))

    if failures:
        log_event(log_file, "worktree.create.failed", failures=failures)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
