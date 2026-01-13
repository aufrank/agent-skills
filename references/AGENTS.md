# AGENTS.md instructions for /home/aufrank

<INSTRUCTIONS>
## Skills
A skill is a set of local instructions stored in a `SKILL.md` file. Frontmatter keeps the skill list in context automatically; no need to enumerate it here. When a task matches or names a skill, open its `SKILL.md` and follow the workflow.
### How to use skills
- Discovery: Use the skill list already present in context; skill bodies live on disk at their listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request from within that skill's directory; don't bulk-load everything.
  3) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks. Execute skill scripts with absolute paths (never by changing into the skill directory). Write outputs to relevant locations in the current project/repo—not into the skill's script directory.
  4) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- User interaction:
  - Favor interactive decisions: use AskUser-style prompts/tools and offer meaningful options when they exist; avoid forcing A/B/C unless there are real alternatives.
- Version control habits (user preference):
  - Commit early/commit often; nag if context is getting too large to summarize into a clear commit message.
  - Work in feature branches by default; plan to summarize commits in PRs (squash/rebase per team norms).
- LSP leverage:
  - Encourage adding language-relevant LSPs to projects and building skills/utilities/CICD hooks that use them; treat LSPs as first-class discovery/navigation tools alongside CLI and agent capabilities.
  - Prefer `pyrefly` for Python and `@typescript/native-preview` for TypeScript when available.
- Context hygiene:
  - Keep context small: summarize long sections; load only what’s needed; avoid deep reference-chasing beyond files linked from `SKILL.md`; pick only relevant variant refs and note the choice.
- Workflow orchestration (general pattern, skills included):
  - Define clear inputs/outputs for each step; capture intermediates on disk so steps can be restarted or reused.
  - Make outputs chainable (machine-readable formats, predictable filenames/paths) so they can feed other scripts or tools; avoid writing into skill directories.
  - Treat flows like DAGs: decide dependencies upfront, then execute in topological order; resume by reading prior outputs instead of re-deriving context.
  - Log decisions and results alongside artifacts (e.g., `progress.txt`, `results.json`) for verifiability and restartability.
- Default agent quality:
  - Prefer machine-readable outputs (JSON/CSV/NDJSON) with minimal schemas/examples; use predictable filenames/paths for chaining.
  - Validate early and often: add lightweight checks (schema validation, lint/format/unit, plan/validate/execute loops) before/after risky steps; cache expensive results/tool metadata to disk with timestamps/keys.
  - Observability: when executing scripts/commands, capture append-only logs (e.g., progress.log/results.json) so the agent can observe execution flow for debugging/learning; keep logs tail-able and compact to protect tokens (summaries over full dumps).
  - Observability by default: keep `progress.log` and `results.json` with commands run, inputs used, outputs produced; include stderr/error summaries for debugging.
  - `results.json` conventions: one per project/task root (predictable path); append entries (don’t clobber) with `id`/`step`, timestamp, inputs (paths/params), outputs (paths, hashes, brief summary), status, notes/errors; read→merge→write; roll by date/task if large and keep a “current” pointer.
  - IDs and discoverability: use grep-friendly IDs (e.g., `task-foo-001`); include git context when present (branch, short SHA) and canonical artifact paths; reuse the same ID across plans/logs/results/commits/branches so `rg`/`git log -G` tie artifacts and code; note commands/scripts for reproducibility.
  - Guardrails in scripts: deterministic flags, explicit errors, timeouts/retries with backoff, input validation; fail fast on missing deps/permissions.
  - Reusability: factor common routines into scripts/templates; avoid writing into skill directories; normalize naming for assets/logs.
  - Trust/permissions: default ASK for writes/deletes; NEVER for creds/destruction; ALWAYS for read/inspect; prefer allowlists over bypassing prompts.
- Continuous improvement:
  - Proactively suggest edits to user-/project-scoped `AGENTS.md` when friction or gaps appear; ask before writing.
  - Suggest improvements to any `SKILL.md` and bundled resources; propose new scripts/templates/assets that reduce repetition or add validation, and keep them in project space (not skill directories).
  - Recommend devex helpers (CLI wrappers, lint/format hooks, setup docs) when they cut future toil; keep suggestions concise and contextual.
- Team and workflow practices:
  - Keep shared guidance alive: maintain team/project `AGENTS.md`/`CLAUDE.md`; add “do/don’t” notes after errors; align on model/settings in repo when appropriate.
  - Plan-first: propose/iterate on plans before auto-accept; keep plan files when useful for traceability.
  - Automate inner loops: add slash-command equivalents or helper scripts for repeated flows (commit/push/PR, lint/format/test) and keep them in-repo; surface them to the agent.
  - Subagents/hooks: suggest specialized sub-flows (simplify/verify) and post-action hooks (formatters, checkers) to harden outputs.
  - Permissions posture: maintain a shared allowlist of safe commands/settings to reduce prompt friction; prefer allowlists over blanket bypass.
  - Shared MCP/tool configs: check in permitted MCP settings/configs so agents can reach org tools (chat/search/analytics/logs) without rediscovery.
  - Where to put utilities: 
    - Repo scripts when they’re project-specific, touch code/assets, or need versioning alongside the codebase.
    - Repo skills when the project needs structured instructions plus scripts/templates for repeated behaviors unique to the repo.
    - General skills when the capability spans projects/users and benefits from shared discovery/versioning.
    - Slash commands for short, high-frequency chat-driven workflows that avoid re-prompting and don’t need to live in the codebase.
- Validation is the unlock:
  - Make success verifiable. Implement validators first when starting new work; keep them current as outputs change.
  - If validation approach is unclear, ask the user how they’d judge success and propose options.
  - Use whatever fits: tests (unit/smoke/fixtures), schema checks, diff/grep invariants, idempotence checks, round-trip or checksum comparisons, command exit codes, or MCP/tool-specific validators.
- Code-mode skill creation (apply when authoring/updating skills):
  - Progressive disclosure: keep `SKILL.md` lean (<500 lines), link to references/templates/scripts instead of inlining; keep references one level deep and point to them explicitly.
  - Files as memory: write large tool/MCP outputs and chat/terminal logs to files; read with `tail`/search instead of pasting blobs; cache MCP tool specs on disk.
  - Scripts over raw tool calls: route MCP via `mcpc --json` and filter (e.g., `jq`); prefer executing scripts with absolute paths over emitting tool calls in-context.
  - Degrees of freedom: split decide → configure → execute; match freedom to task fragility and avoid mixing levels in a single step.
  - Skill structure: gerund/hyphenated naming; frontmatter only `name` and `description` with clear “what” and “when to use”; keep bundles minimal (only resources that unlock execution).
  - Validation and safety: make scripts deterministic/idempotent with explicit errors; use plan/validate/execute loops for risky or batch ops; justify timeouts/constants.
  - Trust policy: Always for reads/listings; Ask for state-changing MCP calls/writes/deletes; Never for credential exfil or destructive/irreversible actions.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
</INSTRUCTIONS>
