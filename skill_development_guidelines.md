# Skill Development Guidelines

## Purpose

- Extend Codex agents with specialized knowledge, workflows, and tool integrations.
- Make agents dependable and restartable through deterministic scripts and clear harness patterns.

## Core Principles

- Progressive disclosure & dynamic context discovery: load only what’s needed; keep bulk context/tool outputs on disk.
- Code-mode bias: prefer deterministic scripts/CLIs for tool use (including MCP via mcpc) over ad-hoc tool calls.
- Eval-driven development: versioned graders/checks; deterministic where possible.
- Repeatability & portability: predictable paths, machine-readable outputs, skills reusable across projects.

## Trust & Safety

- Default read-only; Ask for state changes; Never for creds/destructive actions.
- Use sandboxes/allowlists, explicit errors/timeouts/retries, and append-only logs.

## Plan → Instrument → Execute → Verify (PIEV)

1) Plan: goals, dependencies, success criteria; pick skills/resources and code-mode scripts.
2) Instrument: logs (`progress.log`, `results.json`), evaluators/graders, env/keys, scripts/templates/assets, manifests.
3) Execute: follow `SKILL.md`; run deterministic scripts/tests; use dynamic context discovery to pull only needed slices; keep outputs on disk.
4) Verify: run evaluators/checklists, compare to expectations, capture uncertainties/next steps; log outcomes for restartability.

## Influences

- Cloudflare “code mode”: write code/CLIs against MCP instead of inline tool-calls; LLMs excel at real-world code patterns.
- `mcpc` CLI tool as a uniform bridge: consistent auth/discovery, protocol docs, prompt catalogs, deterministic CLI for tool orchestration.
- Anthropic/Cursor harness patterns for long-running/high-autonomy agents (planning, logging, resumability).

## Tooling / Code-Mode Practices

- Wrap tools in small, composable scripts/CLIs; avoid asking the model to emit raw tool calls.
- Keep interfaces stable: typed inputs, deterministic flags, clear exit codes; store outputs to files for replay/inspection.
- Use `mcpc` (or equivalent) for consistent MCP connectivity, prompt reuse, and piping tool outputs to disk; keep session dirs explicit.
- Balance deterministic graders with model-based graders that have explicit rubrics; keep evaluators versioned.

## Repeatable Workflows

- Authoring: scaffold with `init_skill.py`; keep `SKILL.md` <500 lines; move detail to `references/`; keep deterministic code in `scripts/`.
- Validation: `skills-ref validate <path>`; package via `package_skill.py`; test against intended models and evaluators.
- Execution hygiene: predictable paths, gerund-style names, minimal nesting; avoid clutter in `skills/`.
- Logging/observability: append-only `progress.log`/`results.json`; store slices/prompts/subresponses/finals in run dirs as memory for long runs.

## Slice-Specific Insights

- Code-mode reduces tool-call fragility and token churn; leverage MCP’s uniform docs/auth while keeping execution in code.
- Use on-disk artifacts (manifests, logs, results) to make verify/resume cheap.
- Plan explicitly (triggers, examples, constraints) to reduce variance; summarize tightly while retaining key guidance.
