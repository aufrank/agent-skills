#!/usr/bin/env python3
"""
Shared helpers for Jira mcpc wrappers: auth preflight, MCPC_BIN bridge, and cache/results paths.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

DEFAULT_SERVER = os.environ.get("MCP_SERVER", "https://mcp.atlassian.com/v1/mcp")
DEFAULT_PROFILE = os.environ.get("MCP_PROFILE", "default")
DEFAULT_CLOUD_ID = "ae3605cc-2ea8-41ef-86e8-c7cda3a94bc0"
SKILL_NAME = "querying-jira-programmatically"


def resolve_path(path_str: str) -> Path:
    """Resolve relative paths to cwd; pass through absolute paths."""
    pth = Path(path_str)
    return pth if pth.is_absolute() else Path.cwd() / pth


def _powershell_cmd() -> list[str]:
    """Resolve a PowerShell executable for running .ps1 scripts."""
    override = os.environ.get("POWERSHELL_EXE")
    if override:
        return [override]

    candidates = [
        shutil.which("powershell.exe"),
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "/mnt/c/Program Files/PowerShell/7/pwsh.exe",
        shutil.which("pwsh"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return [str(candidate)]
    sys.stderr.write("PowerShell not found. Install PowerShell or set POWERSHELL_EXE.\n")
    sys.exit(1)


def get_mcpc_cmd() -> list[str]:
    """Return the mcpc invocation as a list, honoring MCPC_BIN for Windows bridges."""
    override = os.environ.get("MCPC_BIN")
    if override:
        p = Path(override)
        suffix = p.suffix.lower()
        if suffix == ".cmd":
            return ["cmd.exe", "/c", str(p)]
        if suffix == ".ps1":
            return [*_powershell_cmd(), "-File", str(p)]
        return [str(p)]

    path = shutil.which("mcpc")
    if not path:
        sys.stderr.write("mcpc not found on PATH. Install or add to PATH, then retry.\n")
        sys.exit(1)
    return [path]


def ensure_auth(server: str, profile: str, session: str) -> None:
    """Verify mcpc profile exists and a lightweight connectivity probe succeeds."""
    profiles_path = Path.home() / ".mcpc" / "profiles.json"
    try:
        data: Dict[str, Any] = json.loads(profiles_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        data = {}

    has_profile = False
    profiles_obj = data.get("profiles", {})
    if isinstance(profiles_obj, dict):
        for server_key, profile_map in profiles_obj.items():
            if not isinstance(profile_map, dict):
                continue
            for profile_name, detail in profile_map.items():
                if not isinstance(detail, dict):
                    continue
                server_url = detail.get("serverUrl") or detail.get("server") or server_key
                name = detail.get("name") or profile_name
                if server_url == server and name == profile:
                    has_profile = True
                    break
            if has_profile:
                break
    else:
        for entry in profiles_obj:
            if not isinstance(entry, dict):
                continue
            if entry.get("server") == server and entry.get("name") == profile:
                has_profile = True
                break

    if not has_profile:
        sys.stderr.write(
            f"No mcpc auth profile '{profile}' for {server}.\n"
            f"Run login yourself in a browser-enabled shell:\n"
            f"  mcpc {server} login --profile {profile}\n"
        )
        sys.exit(1)

    mcpc_cmd = get_mcpc_cmd()
    probe_cmd = [
        *mcpc_cmd,
        "--json",
        "--profile",
        profile,
        session,
        "tools-list",
    ]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
    if probe.returncode != 0:
        sys.stderr.write(
            "mcpc connectivity check failed. Ensure network access and that you are logged in.\n"
            f"Command: {' '.join(probe_cmd)}\n"
            f"stderr: {probe.stderr}\n"
        )
        sys.stderr.write(
            f"Re-run login manually if needed:\n  mcpc {server} login --profile {profile}\n"
        )
        sys.exit(probe.returncode)


def ensure_parent(path: Path) -> None:
    """Create parent directories for output files."""
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def skill_cache_roots() -> dict[str, Path]:
    """Return cache/results roots for this skill (project-aware)."""
    skill_dir = Path(__file__).resolve().parent.parent
    cwd = Path.cwd().resolve()
    home = Path.home().resolve()

    def _is_under(path: Path, maybe_parent: Path) -> bool:
        try:
            path.relative_to(maybe_parent)
            return True
        except ValueError:
            return False

    if _is_under(skill_dir, cwd):
        base = cwd
    elif _is_under(cwd, skill_dir):
        base = skill_dir
    else:
        base = home

    cache_root = base / ".mcpc-skill-caches" / SKILL_NAME
    results_root = base / "results"
    mcp_tools_root = cache_root / "mcp_tools"
    return {
        "base": base,
        "cache_root": cache_root,
        "results_root": results_root,
        "mcp_tools_root": mcp_tools_root,
        "skill_dir": skill_dir,
    }


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def parse_mcpc_payload(raw: Any) -> Any:
    """
    Parse mcpc responses that wrap JSON in content[0].text.
    Returns the parsed payload when possible, otherwise the raw input.
    """
    if isinstance(raw, dict):
        content = raw.get("content")
        if isinstance(content, list) and content and isinstance(content[0], dict):
            text = content[0].get("text")
            if isinstance(text, str):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return raw
    return raw


def timestamped_path(path: Path, enable: bool) -> Path:
    """Append UTC timestamp to filename if enabled."""
    if not enable:
        return path
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return path.with_name(f"{path.stem}.{ts}{path.suffix}")
