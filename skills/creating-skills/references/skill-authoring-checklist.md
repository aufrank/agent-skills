# Skill Authoring Checklist (General)

## Trigger & Naming
- Skill name: lowercase hyphen-case, gerund or action-oriented, ≤64 chars.
- Description: third-person, includes what the skill does + explicit triggers/contexts.

## Structure
- Progressive disclosure: metadata → SKILL.md → references/scripts/templates on demand.
- References one level deep; SKILL.md < 500 lines; avoid duplicate info.
- Forward-slash paths only.

## Content
- Imperative guidance with defaults + escape hatches.
- Decision tree for variants; point to reference files per branch.
- Validation loop: plan → validate → execute; include validators where stakes are high.
- Include trust policy (always/ask/never) and degree-of-freedom separation (decide/configure/execute).
- Document dependencies/timeouts; avoid magic numbers.

## Resources
- Scripts: deterministic, idempotent, explicit inputs/outputs.
- Templates: low-entropy scaffolds (plan.json, results.json, approvals).
- Assets only if used in outputs; no extraneous docs.

## Hygiene
- No time-sensitive statements unless under “old patterns”.
- Consistent terminology.
- Keep outputs/results/plan logs outside the skill bundle when using it.
- Observability: append-only execution logs (progress/errors/results) for debugging/flow insight; share tails/summaries to protect tokens.

## Validation before packaging
- Naming/description rules satisfied.
- References linked from SKILL.md; no deep nesting.
- Scripts executable (`chmod +x` where needed).
- Example tasks or tests run; adjust instructions based on observed gaps.
