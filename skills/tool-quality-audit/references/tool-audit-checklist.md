# Tool Audit Checklist

## Determinism
- Same inputs produce the same outputs.
- Outputs are stable across runs (no random fields).

## Error contracts
- Errors include clear codes and messages.
- Failure modes are documented and reproducible.

## Schema stability
- Output schema is documented and versioned.
- Backward-incompatible changes are avoided or flagged.

## Logging
- Logs are concise and useful for debugging.
- Sensitive data is never logged.
