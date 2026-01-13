# Workflow vs Agent Guidance

## Prefer workflow when
- The task is deterministic and repeatable.
- Inputs/outputs are well-structured.
- You can encode the steps in scripts.

## Prefer agent when
- The task is open-ended or exploratory.
- Tool use requires judgment or dynamic sequencing.
- The environment changes between runs.

## Scaffold hints
- Workflow: define inputs, steps, validators, outputs.
- Agent: define tools, guardrails, artifacts, and resume checkpoints.
