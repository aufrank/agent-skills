# Instrumentation Catalog (Detailed)

## Tests
- Unit tests: logic boundaries, pure functions, input/output invariants.
- Integration tests: multi-module flows, persistence, network boundaries.
- Contract tests: validate schemas and interface expectations.
- Property-based tests: enforce invariants over randomized data.
- Regression tests: lock in behavior after a bug fix.

## Runtime probes
- CLI probes: deterministic commands with explicit output checks.
- Health checks: service startup, endpoint ping, heartbeat assertions.
- Log inspection: structured logs, error counts, warning thresholds.
- Schema dumps: verify migrations or data shape changes.

## Browser and UI
- Playwright flows: critical user paths with assertions.
- Screenshot diffs: layout regressions and visual changes.
- Extension flows: open popup, invoke action, verify results.

## Quality evals
- Retrieval evals: gold queries with expected top-N results.
- Snapshot comparisons: before/after rank lists.
- LLM evals: semantic behavior checks with fixed prompts and scoring.

## Performance and load
- Local load tests: k6/artillery or scripted loops.
- Latency thresholds: p95, p99, error-rate budgets.
- Resource sampling: CPU/memory spikes or steady-state bounds.

## Data integrity
- Row counts/checksums pre/post changes.
- Referential integrity checks and constraint validation.
- Safety gates for destructive operations.
