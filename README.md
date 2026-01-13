# Agent skills
> from @aufrank

Purpose-built skills and references for coding agents. Each skill bundles a `SKILL.md` plus optional scripts/references/assets so agents can load only what they need and execute deterministically.

## Core principles

- Structure skills with clear metadata and lean instructions; push details into references/scripts.
- Use progressive disclosure: metadata first, `SKILL.md` when triggered, resources only as needed.
- Orchestrate work with explicit inputs/outputs, deterministic scripts, and machine-readable artifacts.
- Keep work observable: append-only `progress.log` / `results.json`, reproducible commands, predictable paths.
- Default to safety: Always/Ask/Never trust policy for reads/writes; prefer feature branches and frequent commits.

## Influences and sources

- Code-first execution (scripts over ad-hoc calls) for reliability.
- Dynamic context discovery to minimize tokens and surface only relevant information.
- Degrees-of-freedom tuning: choose specificity to match task fragility.
- Validation mindset: plan → validate → execute loops; iterate after real usage.

## Practical workflows

- Scaffolding: use `skills/*/scripts/init_skill.py` to spin up new skills; follow gerund-style names.
- Development loop: Plan → Instrument → Execute → Validate; keep intermediate outputs on disk for restartability.
- Error handling: deterministic scripts with explicit failures and defaults; avoid deep reference chains.
- Packaging/validation: validate structure before shipping; keep skills self-contained and portable.
- Output norms: prefer JSON/YAML/Markdown for repeatable consumption; log how work was validated.

## Regenerating skill_development_guidelines.md

- Ensure the corpus is up to date: `rlm_prompt_corpus.md` should concatenate references plus all `skills/*/SKILL.md` and `~/.codex/AGENTS.md`.
- Run the RLM pipeline (network on, absolute script path, outputs stay in the repo):

  ```bash
  python /home/aufrank/.codex/skills/slicing-long-contexts/scripts/rlm_cli_runner.py \
    --prompt rlm_prompt_corpus.md \
    --question "Create a skill_development_guidelines document for the aufrank-agent-skills repo: describe purpose, core principles, influences (code-mode/deterministic scripting for tool calls + MCP/mcpc patterns), trust/safety posture, and repeatable workflows using the Plan → Instrument → Execute → Verify pattern. Include slice-specific insights about PIEV and code-mode. Write in actionable prose with bullet lists where helpful." \
    --provider openai \
    --chunk-size 30000 --prefer-headings --max-slices 10 \
    --out-dir rlm_outputs/guidelines_run --run-id rlm-guidelines-001 \
    --with-user-codex-access \
    --summary-cmd-template 'codex {approval_flags} exec --model {model} "$(cat {prompt_path})"' \
    --summary-system-prompt "You are writing skill_development_guidelines.md for the aufrank-agent-skills repository. Summarize sub-responses concisely while preserving guidance on code-mode/deterministic scripting, MCP/mcpc patterns, and the Plan → Instrument → Execute → Verify loop (include slice-specific insights)." \
    --summary-out rlm_outputs/guidelines_run/rlm_summary.txt
  ```

- Copy `rlm_outputs/guidelines_run/rlm_summary.txt` into `skill_development_guidelines.md`.
- Logs: `progress.log`, `results.json`; slices/prompts/sub-responses live under `rlm_outputs/guidelines_run/`.
