# Long-Running Harness Checklist

## Initializer responsibilities
- Confirm environment and dependencies.
- Capture starting state in `progress.log`.
- Write `plan.json` with next-step intent.

## Coder responsibilities
- Execute one small task per session.
- Update `progress.log` and `results.json` after each step.
- Leave a clear "next step" note for resume.

## Resume checks
- Read `progress.log` and `results.json` first.
- Verify last step completed; do not repeat destructive actions.
- Continue with the next smallest unit of work.
