# Eval Roadmap (condensed)

## Suite development
1) Start now, start early.
2) Start with manual tests.
3) Write unambiguous tasks.
4) Cover positive and negative cases.

## Harness development
5) Build a robust eval harness.
6) Design graders thoughtfully (deterministic first, LLM if needed).

## Maintenance
7) Check trajectories to verify graders are fair.
8) Monitor for saturation (capability suites should not hit 100%).
9) Maintain long-term; rotate tasks and fix flaky graders.

## Swiss cheese layers
- Automated evals: fast, repeatable, regression protection.
- Manual transcript review: catch nuanced failures and grader bugs.
- Production monitoring / A-B / feedback: real-world drift and edge cases.
