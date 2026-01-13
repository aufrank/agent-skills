# Skill Development Checklist

Based on `skill_development_guidelines.md`.

## Required
- `SKILL.md` has valid YAML frontmatter with `name` and `description` only.
- Skill name matches folder name and uses lowercase letters, digits, hyphens.
- `SKILL.md` body is concise (<500 lines) with imperative guidance.
- References are one level deep and linked from SKILL.md.

## Structure & portability
- Prefer `text` fences for command examples.
- Avoid bash heredocs; use Python one-liners for file creation when needed.
- Use placeholders `<CODEX_HOME>`, `<REPO_ROOT>`, `<TOOL_HOME>` instead of hard-coded paths.
- Avoid `cd` into skill directories in examples.

## Workflow alignment
- Decide → configure → execute phases are distinct.
- Logging artifacts use deterministic, restartable paths (progress/results/errors).

## Hygiene
- No extra docs (README/CHANGELOG/etc.) inside skill folders.
- Avoid bulk blobs in SKILL.md; move details to references or templates.
