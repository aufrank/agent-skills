#!/usr/bin/env python3
"""
General Skill Initializer - Creates a new skill scaffold

Usage:
    init_skill.py <skill-name> --path <path> [--resources scripts,references,assets,templates] [--examples] [--log-file <log>]

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-new-skill --path skills/public --resources scripts,references,templates
    init_skill.py my-api-helper --path skills/private --resources scripts --examples --log-file /tmp/init.log
    init_skill.py custom-skill --path /custom/location --log-file ./logs/init_skill.log

Notes:
- Normalizes skill names to lowercase hyphen-case (max 64 chars).
- Creates only the requested resource folders; does not write inside this skill.
- Designed for general skill authoring (MCP optional).
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets", "templates"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Clear, third-person, trigger-focused description of what the skill does and when to use it.]
---

# {skill_title}

## Overview
[TODO: 1-2 sentences explaining what this skill enables. Keep concise.]

## Structure (pick one or mix judiciously)
- Workflow-based: decision tree → steps
- Task-based: quick start → task groups
- Capabilities-based: numbered capabilities with defaults and escape hatches
- Reference/guidelines: standards + when to apply them

## Core Guidance
- Keep SKILL.md lean; push bulk detail into references/ one level deep.
- Use decide → configure → execute; do not mix freedom levels.
- Prefer scripts for deterministic work; make them idempotent and explicit about deps/timeouts.
- Add validation + feedback loops; include “old patterns” if legacy behavior matters.
- Observability: log execution steps to append-only files (e.g., progress.log/results.json/errors.log) for debuggability and agent visibility; when sharing in context, use tails/summaries to preserve tokens.

## Resources
Link to any scripts/references/templates/assets you add and state when to read/execute them.

## Validation
[TODO: How to validate this skill (lint, packaging script, exemplar tasks).]
"""

EXAMPLE_SCRIPT = """#!/usr/bin/env python3
\"\"\"Example helper script for {skill_name}

Replace with real automation or delete.
\"\"\"

def main():
    print("This is an example script for {skill_name}")

if __name__ == "__main__":
    main()
"""

EXAMPLE_REFERENCE = """# Reference notes for {skill_title}

Replace with concise reference content (schemas, API tips, workflows).
"""

EXAMPLE_PLAN_TEMPLATE = """{
  "id": "plan-001",
  "intent": "TODO: what this skill engagement aims to achieve",
  "inputs": [],
  "steps": [],
  "trust": "ask|always|never",
  "notes": ""
}
"""

EXAMPLE_RESULTS_TEMPLATE = """{
  "id": "results-001",
  "status": "pending|success|error",
  "inputs": [],
  "outputs": [],
  "errors": [],
  "notes": ""
}
"""


def normalize_skill_name(skill_name: str) -> str:
    """Normalize a skill name to lowercase hyphen-case."""
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name: str) -> str:
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources: str):
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped = []
    seen = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def create_resource_dirs(skill_dir: Path, skill_name: str, skill_title: str, resources, include_examples: bool, log_file: Path | None):
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)
        if resource == "scripts":
            if include_examples:
                example_script = resource_dir / "example.py"
                example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
                example_script.chmod(0o755)
                log("[OK] Created scripts/example.py", log_file)
            else:
                log("[OK] Created scripts/", log_file)
        elif resource == "references":
            if include_examples:
                example_reference = resource_dir / "reference.md"
                example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
                log("[OK] Created references/reference.md", log_file)
            else:
                log("[OK] Created references/", log_file)
        elif resource == "assets":
            placeholder = resource_dir / ".keep"
            placeholder.write_text("assets placeholder\n")
            log("[OK] Created assets/ (placeholder .keep)", log_file)
        elif resource == "templates":
            tpl_dir = resource_dir
            if include_examples:
                (tpl_dir / "plan.json").write_text(EXAMPLE_PLAN_TEMPLATE)
                (tpl_dir / "results.json").write_text(EXAMPLE_RESULTS_TEMPLATE)
                log("[OK] Created templates/plan.json and templates/results.json", log_file)
            else:
                log("[OK] Created templates/", log_file)


def init_skill(skill_name: str, path: str, resources, include_examples: bool, log_file: Path | None):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        resources: Resource directories to create
        include_examples: Whether to create example files in resource directories

    Returns:
        Path to created skill directory, or None if error
    """
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        log(f"[ERROR] Skill directory already exists: {skill_dir}", log_file)
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        log(f"[OK] Created skill directory: {skill_dir}", log_file)
    except Exception as e:
        log(f"[ERROR] Error creating directory: {e}", log_file)
        return None

    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(skill_content)
        log("[OK] Created SKILL.md", log_file)
    except Exception as e:
        log(f"[ERROR] Error creating SKILL.md: {e}", log_file)
        return None

    if resources:
        try:
            create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples, log_file)
        except Exception as e:
            log(f"[ERROR] Error creating resource directories: {e}", log_file)
            return None

    log(f"[OK] Skill '{skill_name}' initialized successfully at {skill_dir}", log_file)
    log("Next steps:", log_file)
    log("1. Edit SKILL.md to complete the TODOs and refine the description.", log_file)
    if resources:
        if include_examples:
            log("2. Customize or delete the example files in scripts/, references/, templates/, and assets/.", log_file)
        else:
            log("2. Add content to requested resource directories as needed.", log_file)
    else:
        log("2. Create resource directories only if needed (scripts/, references/, templates/, assets/).", log_file)
    log("3. Add validation or packaging steps appropriate for your environment.", log_file)

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated list: scripts,references,assets,templates",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Create example files inside the selected resource directories",
    )
    parser.add_argument(
        "--log-file",
        help="Optional path to append a progress log for this initializer run.",
        default=None,
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters."
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = parse_resources(args.resources)
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        sys.exit(1)

    path = args.path

    log_path = Path(args.log_file).resolve() if args.log_file else None

    log(f"Initializing skill: {skill_name}", log_path)
    log(f"   Location: {path}", log_path)
    if resources:
        log(f"   Resources: {', '.join(resources)}", log_path)
        if args.examples:
            log("   Examples: enabled", log_path)
    else:
        log("   Resources: none (create as needed)", log_path)
    if log_path:
        log(f"   Logging to: {log_path}", log_path)

    result = init_skill(skill_name, path, resources, args.examples, log_path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
def log(message: str, log_file: Path | None):
    """Log to stdout and optionally append to a log file."""
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    line = f"[{timestamp}] {message}"
    print(line)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except Exception as e:
            print(f"[WARN] Failed to write log file ({log_file}): {e}")
