#!/usr/bin/env python3
"""
Shared helpers for Notion mcpc wrappers: auth preflight and file outputs.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


def resolve_path(path_str: str) -> Path:
    """Resolve relative paths to cwd; pass through absolute paths."""
    pth = Path(path_str)
    return pth if pth.is_absolute() else Path.cwd() / pth


DEFAULT_SERVER = os.environ.get("MCP_SERVER", "https://mcp.notion.com/mcp")
DEFAULT_PROFILE = os.environ.get("MCP_PROFILE", "default")


def get_mcpc_bin() -> str:
    path = shutil.which("mcpc")
    if not path:
        sys.stderr.write("mcpc not found on PATH. Install or add to PATH, then retry.\n")
        sys.exit(1)
    return path


def ensure_auth(server: str, profile: str, session: str) -> None:
    """Verify mcpc profile exists and a lightweight connectivity probe succeeds."""
    profiles_path = Path.home() / ".mcpc" / "profiles.json"
    try:
        data: Dict[str, Any] = json.loads(profiles_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        data = {}

    # mcpc stores profiles as a map: profiles -> server_host -> profile_name -> detail
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
        # fallback for list-shaped legacy formats
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

    mcpc_bin = get_mcpc_bin()
    probe_cmd = [
        mcpc_bin,
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


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
