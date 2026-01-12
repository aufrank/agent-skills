#!/usr/bin/env python
"""
Run a summarizing reducer over sub-responses using manifest order.

Usage:
  python skills/rlm-cli-runner/scripts/summarize.py --manifest rlm_outputs/manifest.json --subresp-dir rlm_outputs --cmd-template 'codex --model gpt-4o "$(cat {prompt_path})"' --out rlm_outputs/rlm_summary.txt
"""

import argparse
import tempfile
from pathlib import Path

from slice_utils import load_manifest
from subcall_runner import run_subcall


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize sub-responses in manifest order via an LM call.")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json.")
    parser.add_argument("--subresp-dir", required=True, help="Directory containing rlm_subresp_<tag>.txt files.")
    parser.add_argument("--cmd-template", required=True, help="Command template. Vars: {model}, {prompt_path}, {slice_path}, {approval_flags}.")
    parser.add_argument("--model", default="gpt-4o", help="Model identifier.")
    parser.add_argument("--approval-flags", default="", help="Approval/sandbox flags.")
    parser.add_argument("--with-network", action="store_true", help="Add network flags where supported.")
    parser.add_argument("--timeout", type=int, default=None, help="Optional timeout seconds.")
    parser.add_argument("--out", required=True, help="Output path for summarizer result.")
    parser.add_argument("--system-prompt", default="You are a reducer model. Concisely summarize and reconcile the following sub-responses in order. Preserve key details; avoid duplication; surface contradictions.", help="System preamble for the reducer.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    subresp_dir = Path(args.subresp_dir)
    slices = load_manifest(manifest_path)

    parts = [args.system_prompt, "\n\nSub-responses:\n---"]
    for sl in slices:
        sub_path = subresp_dir / f"rlm_subresp_{sl.tag}.txt"
        if not sub_path.is_file():
            continue
        parts.append(f"[{sl.tag} {sl.start}:{sl.end}]\n{sub_path.read_text(encoding='utf-8')}\n")
    prompt_body = "\n".join(parts)

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as tmp:
        prompt_path = Path(tmp.name)
        prompt_path.write_text(prompt_body, encoding="utf-8")

    rc, out = run_subcall(
        args.cmd_template,
        args.model,
        "",
        prompt_path,
        False,
        args.timeout,
        args.approval_flags,
        args.with_network,
        extra_env={},
    )
    Path(args.out).write_text(out or "", encoding="utf-8")
    print(out)
    if rc != 0:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
