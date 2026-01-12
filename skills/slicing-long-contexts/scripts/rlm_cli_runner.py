#!/usr/bin/env python
"""
RLM CLI runner: implements the REPL-style pattern from the RLM paper.
Loads a long prompt from disk, slices it, issues bounded sub-LM calls via a shell
command template, aggregates responses, and writes a final answer file.
Run from a repo root (not the skill dir). Logs append-only lines to
progress.log/results.json by default.
"""

import argparse
import time
from pathlib import Path
from typing import List, Tuple

from aggregator import aggregate
from log_utils import append_log
from slice_utils import Slice, slice_prompt, write_manifest, write_slices
from subcall_runner import run_subcall
from token_utils import estimate_tokens

ALLOWED_ENV_KEYS = {
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "GEMINI_API_KEY",
    "GOOGLE_GEMINI_BASE_URL",
    "CODEX_API_KEY",
    "CODEX_ALLOWED_DOMAINS",
    "OPENAI_ALLOWED_DOMAINS",
    "CODEX_SESSION_DIR",
    "CODEX_HOME",
}

DEFAULT_CMD_TEMPLATE = 'codex {approval_flags} exec --model {model} "$(cat {prompt_path})"'
GEMINI_CMD_NO_MODEL = 'gemini --approval-mode auto_edit "$(cat {prompt_path})"'


def main() -> None:
    parser = argparse.ArgumentParser(description="RLM CLI runner (REPL-style slicing + sub-calls).")
    parser.add_argument("--prompt", required=True, help="Path to the long prompt file.")
    parser.add_argument("--question", required=True, help="Task/question to answer.")
    parser.add_argument("--provider", choices=["openai", "codex", "gemini", "google", "vertex"], default="openai", help="LLM provider to auto-pick defaults.")
    parser.add_argument("--model", default=None, help="Model identifier for the CLI tool.")
    parser.add_argument("--cmd-template", default=None, help="Shell command template. Vars: {model}, {slice_path}, {prompt_path} (optional {question}).")
    parser.add_argument("--chunk-size", type=int, default=30_000, help="Chunk size when no markers are provided.")
    parser.add_argument("--overlap", type=int, default=0, help="Optional overlap (chars) for fixed-size chunking when headings/markers are not used.")
    parser.add_argument("--marker-start", help="Regex for slice start (optional).")
    parser.add_argument("--marker-end", help="Regex for slice end (optional).")
    parser.add_argument("--max-slices", type=int, default=6, help="Max slices/sub-calls to issue.")
    parser.add_argument("--prefer-headings", action="store_true", default=True, help="Prefer Markdown heading-based slices (fallback to markers/chunks).")
    parser.add_argument("--out-dir", default=None, help="Directory for slice/subresp/prompt/final files (default: ./rlm_outputs/<run-id>).")
    parser.add_argument("--output-dir", dest="out_dir", help="Alias for --out-dir.")
    parser.add_argument("--run-id", help="Optional run identifier; included in progress/results logs (default: rlm-YYYYMMDD-HHMMSS).")
    parser.add_argument("--max-subcall-seconds", type=int, default=None, help="Optional timeout per sub-call (seconds); added as a shell timeout prefix.")
    parser.add_argument("--approval-flags", default=None, help="Flags to control CLI approvals/sandbox for sub-calls (e.g., '--sandbox workspace-write --ask-for-approval untrusted' for codex, '--approval-mode auto_edit' for gemini).")
    parser.add_argument("--with-user-codex-access", action="store_true", help="Convenience: append '--add-dir ~/.codex --add-dir ~/.codex/skills' to approval-flags (Codex session dir access).")
    parser.add_argument("--env-file", default=".env", help="Path to .env file (KEY=VALUE) to load and pass to sub-calls (whitelisted keys only).")
    parser.add_argument("--progress-log", default="progress.log", help="Append-only progress log path.")
    parser.add_argument("--results-json", default="results.json", help="Append-only results log path.")
    parser.add_argument("--final-path", default=None, help="Where to write the aggregated final answer (defaults to {out-dir}/rlm_final.txt).")
    parser.add_argument(
        "--sub-system-prompt",
        default=(
            "You are a helper model receiving only one slice of a larger document. "
            "Other slices are handled elsewhere. Answer the root question using ONLY this slice. "
            "Be concise, cite evidence from the slice, and note uncertainty. "
            "If confidence is low or info is missing, stop early and return questions, alternate approaches, "
            "and conditions needed to proceed."
        ),
        help="System preamble prepended to each sub-prompt.",
    )
    parser.add_argument("--code-mode", action="store_true", help="If set, append code-task guidance (validate via scripts/tests, summarize changes, files touched, git state, and reproduction steps).")
    parser.add_argument("--retry-count", type=int, default=0, help="Number of retries per slice on nonzero return code.")
    parser.add_argument("--retry-wait", type=float, default=0, help="Seconds to wait between retries (per slice).")
    parser.add_argument("--skip-on-failure", action="store_true", help="If set, skip failed slices after retries and continue aggregating.")
    parser.add_argument("--verify-slices", help="Comma-separated slice tags to re-run for verification after a successful subcall.")
    parser.add_argument("--dry-run", action="store_true", help="Plan and slice only; skip sub-call execution.")
    parser.add_argument("--greedy-first", action="store_true", help="If set and prompt size <= greedy-max-chars, run a single summarizing call instead of slicing.")
    parser.add_argument("--greedy-max-chars", type=int, default=180_000, help="Max chars allowed for greedy-first path.")
    parser.add_argument("--summary-cmd-template", help="Optional: run a summarizing reducer over all subresponses using this command template.")
    parser.add_argument("--summary-model", default=None, help="Model for summarizing reducer (defaults to --model).")
    parser.add_argument("--summary-system-prompt", default="You are a reducer model. Concisely summarize and reconcile the following sub-responses in order. Preserve key details; avoid duplication; surface contradictions.", help="System preamble for summarizer.")
    parser.add_argument("--summary-out", default=None, help="Output path for summarizer result (defaults to <out-dir>/rlm_summary.txt).")
    parser.add_argument("--warn-tokens", type=int, default=64_000, help="Warn if estimated tokens exceed this value (heuristic).")
    args = parser.parse_args()

    provider_defaults = {
        "openai": {
            "model": "openai/gpt-4o",
            "cmd": DEFAULT_CMD_TEMPLATE,
            "approval": "--sandbox workspace-write --ask-for-approval untrusted",
        },
        "codex": {
            "model": "openai/gpt-4o",
            "cmd": DEFAULT_CMD_TEMPLATE,
            "approval": "--sandbox workspace-write --ask-for-approval untrusted",
        },
        "gemini": {
            "model": "",  # cli bug: omit model flag
            "cmd": GEMINI_CMD_NO_MODEL,
            "approval": "",
        },
        "google": {
            "model": "",  # cli bug: omit model flag
            "cmd": GEMINI_CMD_NO_MODEL,
            "approval": "",
        },
        "vertex": {
            "model": "",  # cli bug: omit model flag
            "cmd": GEMINI_CMD_NO_MODEL,
            "approval": "",
        },
    }
    defaults = provider_defaults.get(args.provider, provider_defaults["openai"])
    if args.provider in ("openai", "codex") and not args.with_user_codex_access:
        args.with_user_codex_access = True
    if args.model is None:
        args.model = defaults["model"]
    if args.cmd_template is None:
        args.cmd_template = defaults["cmd"]
    if args.approval_flags is None:
        args.approval_flags = defaults["approval"]
    run_id = args.run_id or time.strftime("rlm-%Y%m%d-%H%M%S")

    if not args.question or not args.question.strip():
        parser.error("Question is required and cannot be empty.")
    prompt_path = Path(args.prompt)
    if not prompt_path.is_file():
        parser.error(f"Prompt file not found: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8")
    est_tokens = estimate_tokens(prompt, model=args.model)
    progress_log = Path(args.progress_log)
    results_log = Path(args.results_json)
    out_dir = Path(args.out_dir or f"rlm_outputs/{run_id}").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    final_path = Path(args.final_path) if args.final_path else out_dir / "rlm_final.txt"

    extra_env = {}
    env_path = Path(args.env_file).expanduser()
    if not env_path.is_file():
        parser.error(f"Env file not found: {env_path}")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key in ALLOWED_ENV_KEYS:
            extra_env[key] = val
    if "OPENAI_BASE_URL" in extra_env:
        extra_env.setdefault("CODEX_BASE_URL", extra_env["OPENAI_BASE_URL"])
    if args.provider in ("openai", "codex"):
        if not extra_env.get("OPENAI_API_KEY"):
            parser.error("Missing OPENAI_API_KEY in env for provider openai/codex.")
        if not extra_env.get("CODEX_API_KEY"):
            extra_env["CODEX_API_KEY"] = extra_env["OPENAI_API_KEY"]
        codex_home = Path(extra_env.setdefault("CODEX_HOME", str(out_dir / "codex_home")))
        codex_session_dir = Path(extra_env.setdefault("CODEX_SESSION_DIR", str(out_dir / "codex_sessions")))
        codex_home.mkdir(parents=True, exist_ok=True)
        codex_session_dir.mkdir(parents=True, exist_ok=True)
    if args.provider in ("gemini", "google", "vertex"):
        if not (extra_env.get("GEMINI_API_KEY") and extra_env.get("GOOGLE_GEMINI_BASE_URL")):
            parser.error("Missing GEMINI_API_KEY and GOOGLE_GEMINI_BASE_URL in env for provider gemini/google/vertex.")

    run_meta = {"id": run_id}

    append_log(progress_log, {**run_meta, "step": "init", "prompt_path": str(prompt_path), "chars": len(prompt), "chunk_size": args.chunk_size})
    append_log(progress_log, {**run_meta, "step": "token_estimate", "est_tokens": est_tokens, "warn_tokens": args.warn_tokens})
    if est_tokens >= args.warn_tokens:
        print(f"Warning: estimated tokens ~{est_tokens} (>= {args.warn_tokens}). This doc is likely long enough to consider using the 'calling-llms-recursively' RLM runner to divide and conquer.")

    with_network = True

    if args.greedy_first and len(prompt) <= args.greedy_max_chars and args.summary_cmd_template and not args.dry_run:
        greedy_prompt_path = out_dir / "rlm_prompt_greedy.txt"
        greedy_body = (
            f"{args.summary_system_prompt}\n\n"
            f"Root question: {args.question}\n\n"
            f"Full document:\n---\n{prompt}"
        )
        greedy_prompt_path.write_text(greedy_body, encoding="utf-8")
        rc_greedy, out_greedy = run_subcall(
            args.summary_cmd_template,
            args.summary_model or args.model,
            "",
            greedy_prompt_path,
            args.dry_run,
            args.max_subcall_seconds,
            args.approval_flags,
            with_network,
            extra_env,
        )
        final_path.write_text(out_greedy or "", encoding="utf-8")
        append_log(results_log, {**run_meta, "step": "greedy", "rc": rc_greedy, "final_path": str(final_path), "chars": len(prompt)})
        print(out_greedy)
        return

    slices = slice_prompt(
        prompt,
        args.chunk_size,
        args.marker_start,
        args.marker_end,
        args.max_slices,
        prefer_headings=args.prefer_headings,
        overlap=args.overlap,
        base_dir=out_dir,
    )
    write_slices(slices)
    manifest_path = out_dir / "manifest.json"
    write_manifest(slices, manifest_path)
    append_log(progress_log, {**run_meta, "step": "slices_ready", "count": len(slices), "tags": [s.tag for s in slices], "manifest": str(manifest_path)})

    sub_resps: List[Tuple[Slice, str]] = []
    approval_flags = args.approval_flags
    if args.with_user_codex_access:
        codex_dir = Path("~/.codex").expanduser().resolve()
        codex_skills = codex_dir / "skills"
        codex_sessions = codex_dir / "sessions"
        codex_log = codex_dir / "log"
        approval_flags = (
            f"{approval_flags} --add-dir {codex_dir} --add-dir {codex_skills} "
            f"--add-dir {codex_sessions} --add-dir {codex_log}"
        ).strip()
    verify_set = set()
    if args.verify_slices:
        verify_set = {s.strip() for s in args.verify_slices.split(",") if s.strip()}
    for sl in slices:
        prompt_path = out_dir / f"rlm_prompt_{sl.tag}.txt"
        code_footer = ""
        if args.code_mode:
            code_footer = (
                "\n\nFor code tasks: run available scripts/tests to validate; "
                "return a concise summary, files touched, git branch/commit/worktree info, "
                "and how you validated or why you stopped early; include reproduction steps for validation."
            )
        prompt_body = (
            f"{args.sub_system_prompt}\n\n"
            f"Slice info: tag={sl.tag}, span={sl.start}:{sl.end}, chars={len(sl.text)}\n"
            f"Root question: {args.question}{code_footer}\n\n"
            f"Slice:\n---\n{sl.text}"
        )
        prompt_path.write_text(prompt_body, encoding="utf-8")
        attempts = 0
        code, out = run_subcall(
            args.cmd_template,
            args.model,
            args.question,
            prompt_path,
            args.dry_run,
            args.max_subcall_seconds,
            approval_flags,
            with_network,
            extra_env,
        )
        while code != 0 and attempts < args.retry_count:
            attempts += 1
            if args.retry_wait:
                time.sleep(args.retry_wait)
            code, out = run_subcall(
                args.cmd_template,
                args.model,
                args.question,
                prompt_path,
                args.dry_run,
                args.max_subcall_seconds,
                approval_flags,
                True,
                extra_env,
            )
        append_log(
            progress_log,
            {**run_meta, "step": "subcall", "tag": sl.tag, "slice_path": str(sl.path), "prompt_path": str(prompt_path), "rc": code},
        )
        (out_dir / f"rlm_subresp_{sl.tag}.txt").write_text(out or "", encoding="utf-8")
        if code != 0 and not args.dry_run:
            if args.skip_on_failure:
                sub_resps.append((sl, f"[error rc={code}] {out.strip()}"))
                continue
            break
        sub_resps.append((sl, out))
        if code == 0 and sl.tag in verify_set and not args.dry_run:
            v_code, v_out = run_subcall(
                args.cmd_template,
                args.model,
                f"Verify slice {sl.tag}: {args.question}",
                prompt_path,
                args.dry_run,
                args.max_subcall_seconds,
                approval_flags,
                True,
                extra_env,
            )
            append_log(
                progress_log,
                {**run_meta, "step": "verify", "tag": sl.tag, "rc": v_code},
            )
            (out_dir / f"rlm_subresp_{sl.tag}_verify.txt").write_text(v_out or "", encoding="utf-8")
            sub_resps.append((sl, f"[verify rc={v_code}] {v_out.strip()}"))
        if len(sub_resps) >= args.max_slices:
            break

    final_answer = aggregate(sub_resps)
    final_path.write_text(final_answer, encoding="utf-8")
    summary_path = args.summary_out or out_dir / "rlm_summary.txt"
    if args.summary_cmd_template and not args.dry_run:
        reducer_prompt_parts = [args.summary_system_prompt, "\n\nSub-responses:\n---"]
        for sl, resp in sub_resps:
            reducer_prompt_parts.append(f"[{sl.tag} {sl.start}:{sl.end}]\n{resp.strip()}\n")
        reducer_body = "\n".join(reducer_prompt_parts)
        reducer_prompt_path = out_dir / "rlm_reducer_prompt.txt"
        reducer_prompt_path.write_text(reducer_body, encoding="utf-8")
        rc_summary, out_summary = run_subcall(
            args.summary_cmd_template,
            args.summary_model or args.model,
            "",
            reducer_prompt_path,
            args.dry_run,
            args.max_subcall_seconds,
            approval_flags,
            with_network,
            extra_env,
        )
        summary_path = Path(summary_path)
        summary_path.write_text(out_summary or "", encoding="utf-8")
        append_log(results_log, {**run_meta, "step": "summary", "rc": rc_summary, "summary_path": str(summary_path)})
    append_log(results_log, {**run_meta, "step": "final", "final_path": str(final_path), "slices": len(sub_resps)})
    print(final_answer)


if __name__ == "__main__":
    main()
