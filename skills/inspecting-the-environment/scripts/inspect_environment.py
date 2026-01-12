#!/usr/bin/env python3
"""Gather a concise environment briefing for agentic sessions."""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


def run(cmd: Sequence[str]) -> Tuple[bool, str]:
    try:
        completed = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return False, ""
    out = (completed.stdout or "").strip()
    return completed.returncode == 0, out


def detect_shell() -> str:
    shell_env = os.environ.get("SHELL")
    if shell_env:
        return shell_env

    if any(
        key in os.environ
        for key in ("POWERSHELL_DISTRIBUTION_CHANNEL", "PSModulePath", "PSExecutionPolicyPreference")
    ):
        return shutil.which("pwsh") or shutil.which("powershell") or "powershell"

    comspec = os.environ.get("COMSPEC")
    if comspec:
        return comspec

    return ""


def detect_container() -> Tuple[bool, str]:
    markers = [Path("/.dockerenv"), Path("/run/.containerenv")]
    if any(p.exists() for p in markers):
        return True, "container marker file present"
    cgroup = Path("/proc/1/cgroup")
    try:
        if cgroup.exists():
            text = cgroup.read_text()
            if any(token in text for token in ("docker", "kubepods", "containerd", "lxc")):
                return True, "cgroup indicates container"
    except OSError:
        pass
    return False, ""


def detect_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    release = platform.release().lower()
    return platform.system() == "Linux" and "microsoft" in release


def detect_virtual_machine() -> Optional[str]:
    # Linux-specific check
    ok, out = run(["systemd-detect-virt", "--vm"])
    if ok and out:
        return out

    # Windows-specific check
    if platform.system() == "Windows":
        ok, out = run(["systeminfo"])
        if ok:
            manufacturer = ""
            model = ""
            for line in out.splitlines():
                lower = line.lower()
                if "system manufacturer" in lower and ":" in line:
                    manufacturer = line.split(":", 1)[1].strip().lower()
                if "system model" in lower and ":" in line:
                    model = line.split(":", 1)[1].strip().lower()

            combined = f"{manufacturer} {model}"
            vendors = [
                "vmware",
                "innotek gmbh",
                "qemu",
                "kvm",
                "microsoft corporation virtual machine",
                "microsoft corporation hyper-v",
                "xen",
                "parallels",
            ]
            for vendor in vendors:
                if vendor in combined:
                    return f"vm ({vendor} detected in systeminfo)"
            if "virtual machine" in combined:
                return "vm (virtual machine reported by systeminfo)"
    return None


def git_info(root: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"is_repo": False}
    ok, inside = run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"])
    if not ok or inside.lower() != "true":
        return info
    info["is_repo"] = True
    ok, branch = run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"])
    if ok:
        info["branch"] = branch
    ok, upstream = run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    info["upstream"] = upstream if ok else None
    ok, status = run(["git", "-C", str(root), "status", "--porcelain"])
    info["dirty"] = bool(status.strip()) if ok else None
    ok, root_path = run(["git", "-C", str(root), "rev-parse", "--show-toplevel"])
    if ok:
        info["root"] = root_path
    return info


def python_env() -> Dict[str, object]:
    """Return information about the current Python environment."""
    venv = os.environ.get("VIRTUAL_ENV")
    conda = os.environ.get("CONDA_PREFIX")
    # More reliable check for being inside a venv
    in_venv = (sys.prefix != getattr(sys, "base_prefix", sys.prefix)) or bool(venv)
    return {
        "python": sys.executable,
        "version": platform.python_version(),
        "active_venv": venv,
        "active_conda": conda,
        "in_virtualenv": bool(in_venv),
    }


def find_env_dirs(root: Path, names: Sequence[str], max_depth: int = 3, limit: int = 8) -> List[str]:
    """Find directories with common environment-related names."""
    matches: List[str] = []
    try:
        for current, dirnames, _ in os.walk(root):
            rel_parts = Path(current).relative_to(root).parts
            if len(rel_parts) > max_depth:
                dirnames[:] = []
                continue
            if any(part in {".git", "node_modules", "__pycache__", ".cache"} for part in rel_parts):
                dirnames[:] = []
                continue
            for name in list(dirnames):
                if name in names:
                    rel = Path(current, name).relative_to(root)
                    matches.append(str(rel))
                    dirnames.remove(name)
                    if len(matches) >= limit:
                        return sorted(set(matches))
    except PermissionError:
        pass  # Ignore directories we can't read
    return sorted(set(matches))


def find_markdown_dirs(root: Path, max_depth: int, limit: int) -> List[str]:
    """Find directories containing markdown files."""
    md_dirs: List[str] = []
    skip = {".git", "node_modules", "__pycache__", ".cache", "dist", "build", ".venv", "venv", ".tox", "env"}
    try:
        for current, dirnames, filenames in os.walk(root):
            rel_parts = Path(current).relative_to(root).parts
            depth = len(rel_parts)
            dirnames[:] = [d for d in dirnames if d not in skip and depth < max_depth]
            if any(name.lower().endswith(".md") for name in filenames):
                rel = Path(current).relative_to(root)
                md_dirs.append("." if str(rel) == "." else str(rel))
                if len(md_dirs) >= limit:
                    break
    except PermissionError:
        pass  # Ignore directories we can't read
    return sorted(set(md_dirs))


def available_tools(tools: Sequence[str]) -> Dict[str, Optional[str]]:
    return {tool: shutil.which(tool) for tool in tools}


def render_text(data: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append(f"cwd: {data['paths']['cwd']}")
    lines.append(f"os: {data['os']['system']} {data['os']['release']} ({data['os']['machine']})")
    lines.append(f"shell: {data['shell'] or 'unknown'}")
    env = data["environment"]
    lines.append(
        f"env: container={env['in_container']} wsl={env['in_wsl']} vm={env['virtual_machine'] or 'unknown'}"
    )
    git = data["git"]
    lines.append(
        f"git: repo={git['is_repo']} dirty={git.get('dirty')} branch={git.get('branch')} upstream={git.get('upstream')}"
    )
    py = data["python"]
    lines.append(
        f"python: {py['version']} exec={py['python']} venv={py['in_virtualenv']} ({py.get('active_venv') or py.get('active_virtualenv') or py.get('active_conda') or 'none'})"
    )
    lines.append(f"virtualenv_dirs: {', '.join(data['virtualenv_dirs']) or 'none'}")
    lines.append(f"markdown_dirs: {', '.join(data['markdown_dirs']) or 'none'}")
    tool_lines = [f"{k}={('yes' if v else 'no')}" for k, v in data["tools"].items()]
    lines.append("tools: " + ", ".join(tool_lines))
    if data["notes"]:
        lines.append("notes: " + "; ".join(data["notes"]))
    return "\n".join(lines)


def build_report(root: Path, md_limit: int, md_depth: int, tools: Sequence[str]) -> Dict[str, object]:
    in_container, container_reason = detect_container()
    virtual_machine = detect_virtual_machine()
    report: Dict[str, object] = {
        "paths": {"cwd": str(root), "home": str(Path.home())},
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "shell": detect_shell(),
        "environment": {
            "in_container": in_container,
            "container_hint": container_reason or None,
            "in_wsl": detect_wsl(),
            "virtual_machine": virtual_machine,
        },
        "git": git_info(root),
        "python": python_env(),
        "virtualenv_dirs": find_env_dirs(root, names=[".venv", "venv", "env", ".env"]),
        "markdown_dirs": find_markdown_dirs(root, max_depth=md_depth, limit=md_limit),
        "tools": available_tools(tools),
        "notes": [],
    }
    if not report["git"]["is_repo"]:
        report["notes"].append("not in a git repository")
    if report["git"]["is_repo"] and report["git"].get("dirty"):
        report["notes"].append("git working tree has uncommitted changes")
    if report["environment"]["in_container"] and report["environment"]["in_wsl"]:
        report["notes"].append("inside WSL; container detection may be misleading")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize environment constraints and utilities.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory to inspect.")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default=None,
        help="Format for printing the report to stdout. If not provided, nothing is printed to stdout.",
    )
    parser.add_argument("--md-limit", type=int, default=40, help="Maximum markdown-containing directories to list.")
    parser.add_argument("--md-depth", type=int, default=5, help="Maximum directory depth to traverse for markdown.")
    parser.add_argument(
        "--write-json",
        nargs="?",
        const=Path("last_env.json"),
        type=Path,
        help=(
            "Write the JSON report to a file. "
            "Does not print to stdout unless --format is also used. "
            "Defaults to ./last_env.json."
        ),
    )
    parser.add_argument(
        "--extra-tool",
        action="append",
        dest="extra_tools",
        default=[],
        help="Additional binary names to check for (repeatable).",
    )
    args = parser.parse_args()

    default_tools = [
        "git",
        "python",
        "pip",
        "uv",
        "mcpc",
        "rg",
        "ripgrep",
        "grep",
        "jq",
        "node",
        "npm",
        "pnpm",
        "docker",
        "podman",
    ]
    tool_list = default_tools + args.extra_tools
    report = build_report(args.root.resolve(), md_limit=args.md_limit, md_depth=args.md_depth, tools=tool_list)

    if args.write_json:
        write_path = args.write_json if args.write_json.is_absolute() else args.root / args.write_json
        try:
            write_path.parent.mkdir(parents=True, exist_ok=True)
            write_path.write_text(json.dumps(report, indent=2))
            if not args.format:  # Add note only if not printing to stdout
                print(f"Environment report written to {write_path}", file=sys.stderr)
        except OSError as exc:  # pragma: no cover - best effort write
            message = f"failed to write json to {write_path}: {exc}"
            print(message, file=sys.stderr)
            report["notes"].append(message)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif args.format == "text":
        print(render_text(report))


if __name__ == "__main__":
    main()
