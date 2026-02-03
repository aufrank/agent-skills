---
name: defining-instrumentation
description: >
  Define an instrumentation strategy that yields falsifiable evidence a feature or milestone is met. Use
  when asked for test/telemetry/evidence plans, validation criteria, or observability-driven success proof.
---

# Defining Instrumentation

This skill produces an instrumentation strategy that proves (or falsifies) a success criterion with
clear signals, thresholds, and evidence artifacts. It favors deterministic signals, minimal but
sufficient coverage, and local-first execution unless explicitly approved for external systems.

Use this skill when the user asks for:
- instrumentation plans
- validation strategies
- evidence checklists
- “how do we prove this works”
- observability-driven development guidance

Avoid using this skill when the user only needs code changes or implementation details without any
measurement or validation plan.

## Trust posture
- ALWAYS: read/list files, dry-run plans, propose checks.
- ASK: writing scripts, running networked tooling, destructive ops.
- NEVER: credential exfiltration, irreversible deletes, external calls without consent.

## Inputs required (ask if missing)
- Feature or milestone description (goal + success criteria).
- Primary risks or failure modes.
- Constraints: time budget, local-only execution, tooling limits.
- Existing instrumentation or test coverage (if any).

If any input is missing, ask for it before producing a final plan. If the user wants a fast start,
produce a draft plan and explicitly mark assumptions.

## Outputs (deliverables)
- Instrumentation Plan (primary artifact)
- Evidence Checklist with commands/methods, expected outputs, and thresholds
- Fallback Plan if primary signals are blocked or flaky

## Operating principles
- Triangulate evidence for high stakes: at least two independent signals.
- Prefer deterministic signals: tests, schema checks, invariant probes.
- Make failures actionable: each signal suggests a likely fix.
- Keep it local unless approved: avoid external services by default.
- Instrument before execute: plan signals first, then run.

## Degrees of freedom
- High (explore): gather risks, map success criteria, propose signals.
- Medium (shape): select minimal set of signals, define thresholds.
- Low (execute): provide commands to run; do not run unless asked.

Keep phases separate: decide → configure → execute.

## Core workflow (use this every time)

### 1) Clarify scope and success criteria
- Restate the goal and success criteria in your own words.
- Identify top 1–2 risks or failure modes.
- Confirm constraints and tooling.

Checklist:
- What must be true for success?
- What could go wrong?
- What evidence would convince a skeptical reviewer?

### 2) Map criteria to signals
For each success criterion, pick at least one signal. For each top risk, add a signal.
Select the smallest set that still convinces.

Signal selection rules:
- Each criterion has a primary signal with a pass/fail threshold.
- Each critical risk has a dedicated signal.
- Add a fallback if a primary signal may be flaky or blocked.

### 3) Specify evidence artifacts
For each signal, define:
- Command/Method
- Expected output or threshold
- Evidence artifact (e.g., test output, log snippet, snapshot file)

### 4) Assemble the instrumentation plan
Use the template in this file and produce:
- Primary signals (must pass)
- Secondary signals (nice-to-have)
- Fallbacks
- Validation notes

### 5) Review for sufficiency
- Are the signals reproducible locally?
- Are thresholds explicit?
- Are signals independent when stakes are high?
- Are failure modes actionable?

If not, adjust before finalizing.

## Signal catalog (core summary)
Use this list to select signals. Prefer deterministic signals first.

### Tests
- Unit tests for logic boundaries
- Integration/contract tests for interfaces
- Property-based tests for invariants
- Regression tests for prior bugs

### Runtime probes
- CLI outputs, migrations, schema dumps
- Health checks (startup, endpoint ping)
- Log inspection (error counts, warnings)

### Browser and UI
- Playwright flows with assertions
- Screenshot diffs for layout regressions
- Smoke tests for extension/popup flows

### Quality evals
- Retrieval relevance evals with gold queries
- Snapshot diffs for before/after ranking
- LLM eval harnesses for semantic behavior

### Performance and load
- Local load tests or scripted loops
- Latency/error thresholds (p95, error rate)
- CPU/memory sampling if available

### Data integrity
- Row counts/checksums pre/post
- Referential integrity checks
- Guardrails for destructive operations

## Strategy selection checklist
- Map each success criterion to a signal.
- Add a signal for each top risk.
- Define explicit thresholds (pass/fail, error budget, p95).
- Ensure reproducible and local execution.
- Add a fallback for each critical check.

## Evidence template (use in every response)

Instrumentation Plan
Goal:
Primary risks:

Primary signals (must pass):
1) Signal:
   Command/Method:
   Expected output/threshold:
   Evidence artifact:

Secondary signals (nice-to-have):
1) Signal:
   Command/Method:
   Expected output/threshold:

Fallbacks if blocked:
1) ...

Validation notes:
- How evidence will be recorded (logs, snapshots, test output).

## Examples (condensed)

Example: New tool behavior
- Primary: contract test for payload shape
- Primary: smoke test calling tool with known data
- Secondary: log inspection for enqueue

Example: Search relevance tweak
- Primary: golden query eval with top-N expected
- Primary: snapshot diff for ranking changes
- Secondary: manual spot-check (3 queries)

Example: UI change
- Primary: Playwright flow asserts render + action
- Primary: screenshot diff for regressions
- Secondary: console log scan

Example: Background job scheduling
- Primary: startup health check
- Primary: log probe for schedule interval
- Secondary: data probe for updated rows

Example: SQL guardrails
- Primary: negative tests for blocked statements
- Primary: positive tests for safe queries
- Secondary: timeout guardrail validation

## Escalation guidance
If constraints or missing tooling block strong evidence:
- Propose minimal additional tooling.
- Offer a weaker deterministic fallback.
- Call out residual risks explicitly.

## Definition of done
- A concrete, runnable instrumentation plan exists.
- Each success criterion is mapped to evidence.
- Risks have explicit checks and thresholds.
- Fallbacks listed for flaky/blocked signals.

## Specialist references (optional)
Use these only if deeper context is needed:
- references/strategist-core.md
- references/instrumentation-catalog.md
- references/examples.md
- templates/instrumentation-plan.md
