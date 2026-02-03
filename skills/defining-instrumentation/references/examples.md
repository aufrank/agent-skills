# Examples

## New tool behavior
- Contract test for payload shape.
- Smoke test calling the tool with known data.
- Log inspection to confirm enqueue.

## Search relevance tweak
- Offline eval: golden queries with expected top-N URLs.
- Before/after snapshot diff for ranking changes.
- Manual spot check of 3 high-risk queries.

## Extension popup UX change
- Playwright flow: click action, verify popup renders, run a command.
- Screenshot diff for layout regressions.
- Console log scan for errors.

## Background job scheduling
- Health check: startup runs without warnings.
- Log probe: job enqueued at expected interval.
- Data probe: rows updated in the last N minutes.

## SQL guardrail changes
- Negative tests for blocked statements.
- Positive tests for safe queries (SELECT/CTE).
- Timing guardrail validation (query timeout).
