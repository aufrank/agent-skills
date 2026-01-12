---
name: slicing-long-contexts
description: "Run Recursive Language Model-style map/reduce workflows via CLI (with codex or gemini: load long/complex inputs as data, slice by headings/chunks, issue sub-LM calls on slices, and optionally run a summarizing reducer; supports dry-run planning and divide-and-conquer for large or dense tasks."
---

# RLM CLI Runner

Use this skill to replicate the paper's REPL-based RLM pattern: treat the long prompt as data in a Python REPL, peek/slice it with code, and spawn recursive sub-LM calls (codex or gemini) on targeted snippets. Designed for dynamic context (write big outputs to files; read with tail/rg) and AGENTS preferences (plans/logs/results outside the skill dir).

Trust posture: ASK for writes/network; keep sandbox workspace-write unless a task requires more. `--with-network` toggles codex/gemini network; leave it off unless needed.

## Fast path (doc summarization)

For “slice + summarize a long corpus into one doc” (headings, codex, network on):

```bash
python /home/aufrank/.codex/skills/slicing-long-contexts/scripts/rlm_cli_runner.py \
  --prompt <corpus-file> \
  --question "Write <target-doc> covering <topics> in concise bullets." \
  --provider openai \
  --chunk-size 30000 --prefer-headings --max-slices 6 \
  --out-dir rlm_outputs/<run_name> --run-id <run_name> \
  --with-user-codex-access \
  --summary-cmd-template 'codex {approval_flags} exec --model {model} "$(cat {prompt_path})"' \
  --summary-system-prompt "You are writing <target-doc>. Combine sub-responses into a concise, structured, actionable output." \
  --summary-out rlm_outputs/<run_name>/rlm_summary.txt
```

Then copy `rlm_outputs/<run_name>/rlm_summary.txt` into your target doc. Use absolute script paths; never `cd` into the skill dir or write outputs there.

Cleanup helper (separate script):

```bash
python /home/aufrank/.codex/skills/slicing-long-contexts/scripts/cleanup_outputs.py --target runs|slices|prompts|responses|summary|final|manifest|all
```

## When to use

- You have a long or complex input (multi-doc reasoning, codebase understanding, tool schemas, long chat history, terminal logs) and want RLM-style recursion to plan and execute sub-queries programmatically.
- You want a coordinator (root depth 0) that slices, runs sub-calls, and optionally a reducer pass to stitch/summarize.
- If the context clearly fits in the base LM and is low-density, consider a direct call; otherwise prefer this skill for dense inputs or when you need reproducible map/reduce artifacts.

## Inputs / Outputs

- **Inputs**: prompt file path, task/question, sub-call budget (count/time), recursion depth (max 1–2), target LM CLI (`codex`/`gemini`).
- **Outputs**: `FINAL_ANSWER` text; append-only `progress.log` / `results.json` in the repo root (not in `skills/`); slice files in `<out-dir>/rlm_slice_<tag>.txt`; per-subcall prompts in `<out-dir>/rlm_prompt_<tag>.txt`; sub-responses in `<out-dir>/rlm_subresp_<tag>.txt`; final in `<out-dir>/rlm_final.txt` (default `./rlm_outputs`).

## Trust / bounds

- ASK for writes; keep recursion depth <=2; cap sub-calls (e.g., max 5) and wall time. Prefer batching ~200k chars per sub-call to avoid thousands of calls (per paper’s Qwen prompt).
- Keep tmp paths deterministic; avoid leaking full prompt to sub-calls—send only slices.
- Use coding-capable models for sub-calls; weak coding models behave poorly per paper.

## Prereqs

- `uv` env active (`.venv` exists); run with `UV_CACHE_DIR=.uv-cache uv run ...`.
- CLI LMs configured: `codex` or `gemini`.
- Long prompt stored as a file (e.g., `prompt.txt`).

## Workflow (plan → instrument → execute → verify)

1) **Plan**: Define the question, budget (max sub-calls/time), depth limit (1–2), and slice strategy (markers vs fixed chunks).

1) **Instrument dynamic context**:

- Set log paths (repo root): `progress.log`, `results.json`; append entries (id/step, inputs, outputs, status). Example log line: `{"id":"rlm-run-001","step":"subcall","tag":"h0","rc":0}`.
- Choose output dir (absolute or repo-relative; defaults to `<cwd>/rlm_outputs`): slices, prompts, sub-responses, final answer live here (configurable via `--out-dir/--output-dir`). Avoid writing inside `skills/`.
  - Note context stats for the REPL prompt: total chars, planned chunk sizes; record in log.

1) **Load prompt into REPL (root, depth 0)**:

   ```bash
   UV_CACHE_DIR=.uv-cache uv run python -q <<'PY'
   from pathlib import Path
   prompt = Path("prompt.txt").read_text()
   print("chars", len(prompt))
   print(prompt[:200])  # peek
   PY
   ```

   Keep `prompt` as the REPL variable; do not pipe the entire text to LMs.

2) **Plan slices** (programmatic): use markers or fallback to fixed-size chunking. See `references/repl-snippets.md`.
   - Optional: use heading-based slices (`--prefer-headings`) or install markdown tooling (`scripts/setup_markdown_tools.sh`) for richer parsing.

3) **Issue sub-calls on slices (depth=1)**:

   ```bash
   slice_file=/tmp/rlm_slice_ch1.txt
   UV_CACHE_DIR=.uv-cache uv run python - <<'PY'
   from pathlib import Path
   prompt = Path("prompt.txt").read_text()
   start = prompt.find("Chapter 1")
   end = prompt.find("Chapter 2")
   if start == -1:  # marker missing -> fallback to fixed chunk
       start, end = 0, 4000
   Path("/tmp/rlm_slice_ch1.txt").write_text(prompt[start:end])
   PY

   codex --model gpt-4o "Sub-task: list items before the Great Catastrophe in this slice.\n---\n$(cat $slice_file)" > /tmp/rlm_subresp_ch1.txt
   ```

   - Label each sub-response; keep a list in REPL (`sub_responses = {"ch1": Path(...).read_text()}`).
   - Batch slices when possible (target ~200k chars per call) to reduce call count.
   - Use `tail -n 40` to inspect long outputs instead of pasting everything.

4) **Aggregate + verify in REPL**:

   ```bash
   UV_CACHE_DIR=.uv-cache uv run python - <<'PY'
   from pathlib import Path
   subs = {
       "ch1": Path("/tmp/rlm_subresp_ch1.txt").read_text(),
       "ch3": Path("/tmp/rlm_subresp_ch3.txt").read_text(),
   }
   final = f"From chapter 1: {subs['ch1']}\nFrom chapter 3: {subs['ch3']}"
   Path("/tmp/rlm_final.txt").write_text(final)
   print(final)
   PY
   ```

   Optionally run a verification sub-call on the same slice to sanity-check a claim. Keep the final answer in a variable/file (analogous to FINAL_VAR in the paper) and emit once.

5) **Emit final answer**: print `FINAL_ANSWER`; log paths used and remaining budget. Stop if quality is adequate.

## Patterns to reuse

- Peek before sending: `print(prompt[:N])`, regex hits, newline splits.
- Keyword/TOC chunking: `prompt.split("Chapter 2")`, regex finditer for headers.
- Fixed-size fallback when markers are missing.
- Dynamic context: write big tool outputs to files; inspect with `tail`/`rg`; avoid copying whole blobs into prompts.
- Long docs (PRD/tech design/research/PDF): ask if divide-and-conquer is acceptable; draft a slice prompt that states per-chunk goals and aggregation plan; run `--dry-run` to choose headings vs fixed-size chunking before spending real sub-calls.
- Use cases beyond “large docs”: multi-document synthesis; codebase/source understanding; loading tool schemas/logs on demand; recovering detail from chat history by saving it to files; domain-scoped skills (sales/finance/etc.) to keep context tight.
- Reliability: use `--retry-count/--retry-wait` to recover transient failures; `--skip-on-failure` to keep going; `--verify-slices` for spot checks; `--overlap` to add coherence between fixed chunks; rerun/verify helpers live in `scripts/`.
- Sub-call labeling: keep per-slice tags so aggregation is deterministic.
- Long outputs: store sub-call outputs in variables/files and stitch; avoid regenerating from scratch.
- Verification: run spot-check sub-calls on the same slice; stop when adequate to cap variance.
- Cost/risk: sequential sub-calls are slower; async would help but is out-of-scope here—budget accordingly.

## References

- `references/repl-snippets.md` — slicing/search/compose helpers and logging snippets.
- `references/dynamic_context_from_cursur.md` — dynamic context discovery pattern to minimize tokens.
- `scripts/rlm_cli_runner.py --help` — view runnable options (slicing modes, code-mode, system prompt, logs).
- `scripts/setup_markdown_tools.sh` — optional markdown parsing helpers via uvx.
- `scripts/rerun_slice.py` / `scripts/verify_slice.py` — rerun or spot-check saved slice prompts.
- `scripts/slice_utils.py` (CLI): slice prompt → slices + manifest.
- `scripts/subcall_runner.py` (CLI): run one prompt with retries/skip.
- `scripts/aggregator.py` (CLI): aggregate sub-responses from manifest order.
- `scripts/summarize.py` (CLI): run a summarizing reducer over sub-responses in manifest order.
- `scripts/estimate_tokens.py` (CLI): estimate tokens for files (heuristic, optional tiktoken).

### Default vs advanced usage

- Default: use `rlm_cli_runner.py` to orchestrate slicing → subcalls → aggregation; it writes a manifest and all artifacts (slices/prompts/subresponses/final).
- Advanced (compose manually):
  1. `slice_utils.py --prompt ... --out-dir ...` → slices + `manifest.json`
  2. `subcall_runner.py --prompt rlm_prompt_<tag>.txt --cmd-template ...` → run one slice (retries/skip supported)
  3. `aggregator.py --manifest manifest.json --subresp-dir ... --out final.txt` → ordered reduce (optional dedup)
  4. `rerun_slice.py` / `verify_slice.py` for targeted reruns/spot-checks
  5. `summarize.py --manifest manifest.json --subresp-dir ... --cmd-template ... --out summary.txt` for a summarizing reducer

## Usage notes

- Provider auto-sets defaults: `--provider openai|codex|gemini|google|vertex` chooses cmd template, approval flags, and model (openai/codex → `openai/gpt-4o`; gemini/google/vertex → omit `--model` for now due to CLI bug). Override with `--model`/`--cmd-template` if truly needed.
- Env file defaults to `.env` (required) and must include necessary API keys/URLs (e.g., `OPENAI_API_KEY`, `CODEX_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_GEMINI_BASE_URL`) from the runner allowlist. Point elsewhere with `--env-file <path>`. For openai/codex providers both OPENAI_API_KEY and CODEX_API_KEY must be set; for gemini/google/vertex both GEMINI_API_KEY and GOOGLE_GEMINI_BASE_URL must be set.
- Defaults tuned for docs: headings preferred, chunk size 30k, max slices 6, approval flags set for Codex workspace-write.
- If `--run-id` is omitted, runner uses `rlm-YYYYMMDD-HHMMSS` and writes to `rlm_outputs/<run-id>`.
- Codex example cmd template: `codex --sandbox workspace-write --ask-for-approval untrusted exec --model {model} "$(cat {prompt_path})"`
- Gemini example cmd template: `gemini --approval-mode auto_edit --model {model} "$(cat {prompt_path})"`
- If Codex needs access to ~/.codex, add a writable dir: `--add-dir ~/.codex` (and `--add-dir ~/.codex/skills` if needed). Runner convenience: `--with-user-codex-access` appends these.
- Greedy path: `--greedy-first` will run a single summarizing call (using `--summary-cmd-template`) when the prompt fits under `--greedy-max-chars` (default 180k), skipping slicing.
- Token warning: runner estimates tokens (heuristic) and warns at `--warn-tokens` (default 64k) that the doc is likely long enough to divide and conquer.
- Note: In WSL, symlinks to /mnt/c may still be blocked by NTFS perms/sandbox. Prefer WSL-local ~/.codex/.gemini or mount C: with metadata so the CLI can write sessions.

## Common commands

- Codex doc summarization (headings, network on):

  ```bash
  python /home/aufrank/.codex/skills/slicing-long-contexts/scripts/rlm_cli_runner.py \
    --prompt corpus.md \
    --question "Summarize this corpus into <target doc> with concise bullets." \
    --provider openai \
    --chunk-size 30000 --prefer-headings --max-slices 6 \
    --out-dir rlm_outputs/run1 --run-id run1 \
    --with-user-codex-access \
    --summary-cmd-template 'codex {approval_flags} exec --model {model} "$(cat {prompt_path})"' \
    --summary-system-prompt "You are writing <target doc>. Combine sub-responses into a concise, structured, actionable output." \
    --summary-out rlm_outputs/run1/rlm_summary.txt
  ```

- Gemini variant (network on by default):

  ```bash
  python /home/aufrank/.codex/skills/slicing-long-contexts/scripts/rlm_cli_runner.py \
    --prompt corpus.md \
    --question "Summarize this corpus into <target doc> with concise bullets." \
    --provider gemini \
    --chunk-size 30000 --prefer-headings --max-slices 6 \
    --out-dir rlm_outputs/run1 --run-id run1 \
    --summary-cmd-template 'gemini --approval-mode auto_edit "$(cat {prompt_path})"' \
    --summary-system-prompt "You are writing <target doc>. Combine sub-responses into a concise, structured, actionable output." \
    --summary-out rlm_outputs/run1/rlm_summary.txt
  ```

- Override template that needs `{question}` inline:

  ```bash
  python /home/aufrank/.codex/skills/slicing-long-contexts/scripts/rlm_cli_runner.py \
    --prompt prompt.txt --question "List blockers" \
    --cmd-template 'codex {approval_flags} exec --model {model} "{question}\n\n$(cat {prompt_path})"'
  ```

Note: `--prompt` must point to an existing file and `--question` cannot be empty; the runner will error otherwise.

## Logging helpers

- Runner logs to `progress.log` (init, slices_ready, subcall) and `results.json` (final) using JSONL; optionally set `--run-id` to tag all entries.
- To append manual notes in the same format, use the helper:  

  ```bash
  python skills/rlm-cli-runner/scripts/log_entry.py --log progress.log --run-id rlm-run-001 --step note --kv message="Paused for approval" --timestamp
  ```
