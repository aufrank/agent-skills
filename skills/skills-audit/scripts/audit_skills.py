#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    message: str


FRONTMATTER_RE = re.compile(r"^---\s*$")
NAME_RE = re.compile(r"^[a-z0-9-]+$")
PLACEHOLDER_RE = re.compile(r"<CODEX_HOME>|<REPO_ROOT>|<TOOL_HOME>")
HARD_PATH_RE = re.compile(r"(/Users/|/home/|~/.codex|C:\\\\)")
FENCE_BASH_RE = re.compile(r"```bash")
CD_INSTRUCTIONS_RE = re.compile(r"\bcd\s+[^\\n]+")


def iter_skill_dirs(root: Path) -> Iterator[Path]:
    for skill_dir in root.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            yield skill_dir


def load_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def find_frontmatter(lines: list[str]) -> tuple[int, int] | None:
    if not lines or not FRONTMATTER_RE.match(lines[0]):
        return None
    for idx in range(1, len(lines)):
        if FRONTMATTER_RE.match(lines[idx]):
            return 0, idx
    return None


def parse_frontmatter(lines: list[str]) -> dict[str, str]:
    fm = {}
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"')
    return fm


def audit_frontmatter(skill_dir: Path, findings: list[Finding]) -> None:
    skill_md = skill_dir / "SKILL.md"
    lines = load_lines(skill_md)
    fm_bounds = find_frontmatter(lines)
    if fm_bounds is None:
        findings.append(Finding(str(skill_md), 1, "frontmatter", "Missing YAML frontmatter."))
        return
    start, end = fm_bounds
    fm_lines = lines[start + 1 : end]
    fm = parse_frontmatter(fm_lines)
    if "name" not in fm or "description" not in fm:
        findings.append(Finding(str(skill_md), 1, "frontmatter", "Missing name/description."))
    for key in fm.keys():
        if key not in {"name", "description", "metadata", "license", "compatibility", "allowed-tools"}:
            findings.append(Finding(str(skill_md), 1, "frontmatter", f"Unexpected key: {key}"))
    name = fm.get("name", "")
    if name and not NAME_RE.match(name):
        findings.append(Finding(str(skill_md), 1, "naming", f"Invalid name: {name}"))
    if name and name != skill_dir.name:
        findings.append(Finding(str(skill_md), 1, "naming", f"Name does not match folder: {skill_dir.name}"))
    if len(lines) > 500:
        findings.append(Finding(str(skill_md), 1, "length", "SKILL.md exceeds 500 lines."))


def audit_portability(skill_dir: Path, findings: list[Finding]) -> None:
    skill_md = skill_dir / "SKILL.md"
    lines = load_lines(skill_md)
    for idx, line in enumerate(lines, start=1):
        if FENCE_BASH_RE.search(line):
            findings.append(Finding(str(skill_md), idx, "portability", "bash fence used; prefer text fence."))
        if HARD_PATH_RE.search(line) and not PLACEHOLDER_RE.search(line):
            findings.append(Finding(str(skill_md), idx, "portability", "Hard-coded path; use placeholders."))
        if CD_INSTRUCTIONS_RE.search(line):
            findings.append(Finding(str(skill_md), idx, "portability", "Avoid cd into skill directories."))


def audit_references(skill_dir: Path, findings: list[Finding]) -> None:
    references = skill_dir / "references"
    if not references.exists():
        return
    for path in references.rglob("*.md"):
        if path.parent != references:
            findings.append(Finding(str(path), 1, "references", "References should be one level deep."))


def audit_extra_docs(skill_dir: Path, findings: list[Finding]) -> None:
    for name in ["README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"]:
        path = skill_dir / name
        if path.exists():
            findings.append(Finding(str(path), 1, "hygiene", f"Unexpected extra doc: {name}"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit skill folders for guideline compliance.")
    parser.add_argument("--root", default="skills", help="Root directory containing skill folders.")
    parser.add_argument("--guidelines", default="skill_development_guidelines.md", help="Guidelines file path.")
    parser.add_argument("--out", default="audit_results.json", help="Output JSON report path.")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    findings: list[Finding] = []
    for skill_dir in iter_skill_dirs(root):
        audit_frontmatter(skill_dir, findings)
        audit_portability(skill_dir, findings)
        audit_references(skill_dir, findings)
        audit_extra_docs(skill_dir, findings)

    report = {
        "root": str(root),
        "guidelines": str(Path(args.guidelines)),
        "count": len(findings),
        "findings": [finding.__dict__ for finding in findings],
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for finding in findings:
        print(f"{finding.path}:{finding.line} [{finding.rule}] {finding.message}")

    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
