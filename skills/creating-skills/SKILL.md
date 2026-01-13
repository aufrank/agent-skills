---
name: creating-skills
description: >
  General skill authoring and improvement. Use when creating or updating any skill (with or without MCP),
  selecting structure, generating scaffolds, or packaging resources (scripts/references/assets/templates)
  that follow progressive disclosure, deterministic execution, and restartable artifacts.
---

# Creating Skills (General)

This skill helps you design and ship skills that are concise, restartable, and discoverable—whether or not MCP is involved. Assume the model is capable; focus on structure, guardrails, and on-disk artifacts.

## Quick Start

- Pick scope + name first (gerund, hyphen-case, ≤64 chars). Examples: `creating-skills`, `auditing-permissions`.
- Run the scaffold script when starting fresh: `python creating-skills/scripts/init_skill.py <skill-name> --path <target> [--resources scripts,references,assets,templates] [--examples]`.
- Keep SKILL.md under 500 lines; push bulk info into `references/` or `templates/`; keep references one level deep.
- Use the decide → configure → execute pattern; never mix freedom levels in one step.
- Persist intent/results: `plan.json` (intent), `progress.log` (append-only log), `results.json` (structured outputs), `errors.log` (diagnostics). Do not write inside skill bundles during use.
- Observability: log execution steps/commands to append-only files so the agent can observe flow; use tail/grep/summarize instead of dumping entire logs into context to stay token-efficient.

## Trust Policy

- ALWAYS: read/list files, list tools, dry-run planning.
- ASK: writes, packaging, networked installs, destructive actions.
- NEVER: credential exfil, irreversible deletes, running untrusted code.

## Degrees of Freedom

- High (explore): gather examples, choose structure, confirm triggers.
- Medium (shape): fill templates, parameterize scripts, generate plan.json.
- Low (execute): run deterministic scripts, validators, packagers.

Keep phases separate: decide → configure → execute.

## Minimal Workflow (new skill)

1) **Clarify scope & triggers**
   - Define what the skill does, when it triggers, and its trust posture.
   - Normalize name; ensure description includes both capability and triggers.

2) **Scaffold**
   - Run `scripts/init_skill.py` (see Quick Start) into the target path (not inside this skill).
   - Choose only needed resources; delete placeholders you won’t use.

3) **Design info architecture**
   - Keep SKILL.md lean; link to references one level deep.
   - Use templates for plan/results/approvals; keep them low-entropy.
   - For code-heavy skills, prefer scripts over inline tool calls; make scripts idempotent and explicit about deps/timeouts.

4) **Author content**
   - Frontmatter: only `name` + `description` (third person, triggers included).
   - Body: imperative guidance, decision trees, checklists, and pointers to references/scripts/templates.
   - Include validation/feedback loops and “old patterns” if legacy behavior matters.

5) **Validate**
   - Run your own checks or add a validator script; ensure naming, description quality, path hygiene (forward slashes), and reference depth.
   - Add quick self-tests or exemplar tasks if possible.

6) **Package / iterate**
   - If packaging, zip the skill directory (excluding transient artifacts); keep a `dist/` outside the skill folder.
   - After usage, update SKILL.md or references based on observed gaps; log changes in `progress.log` (outside the skill).

## Content Patterns (apply as needed)

- **Progressive disclosure**: metadata → SKILL.md → references/scripts/templates on demand.
- **Decision trees**: route to the right reference/script; state defaults and escape hatches.
- **Templates**: prefer JSON/YAML/Markdown scaffolds over prose; keep strict vs flexible variants clear.
- **Validation loops**: plan → validate → execute; favor machine-checkable validators.
- **Dynamic context discovery**: write large outputs/logs to files; read with `head`/`tail`/`grep` as needed; avoid dumping blobs into context.
- **Execution logs**: keep append-only logs (progress/errors/results) for debuggability and learning; when sharing in context, prefer succinct summaries or tails to conserve tokens.

## References

- For deeper patterns and examples, open:
  - `references/skill-authoring-checklist.md` — condensed checklist and triggers
  - `references/templates/plan.json` — plan scaffold (edit per skill)
  - `references/templates/results.json` — results scaffold with `id` and `step`

Keep references succinct; add domain-specific guides per skill, one level deep.
