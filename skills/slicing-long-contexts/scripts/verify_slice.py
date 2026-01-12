#!/usr/bin/env python
"""
Verify a saved RLM slice prompt by re-running it with a verification preamble.

Usage:
  python skills/rlm-cli-runner/scripts/verify_slice.py --prompt rlm_outputs/skill_refs/rlm_prompt_h0.txt --cmd-template 'codex --model gpt-4o "$(cat {prompt_path})"'
"""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def run_subcall(cmd_template: str, model: str, prompt_path: Path, timeout: int | None, approval_flags: str, with_network: bool) -> tuple[int, str]:
    cmd = cmd_template.format(
        model=model,
        prompt_path=prompt_path,
        slice_path=prompt_path,
        approval_flags=approval_flags.strip(),
    )
    if with_network:
        if "gemini " in cmd and "--network-access" not in cmd:
            cmd = cmd.replace("gemini ", "gemini --network-access enabled ", 1)
        if "codex " in cmd and "network_access=true" not in cmd:
            cmd = cmd.replace("codex ", "codex -c sandbox_workspace_write.network_access=true ", 1)
    if timeout:
        cmd = f"timeout {timeout}s {cmd}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=os.environ.copy())
    return res.returncode, res.stdout if res.stdout else res.stderr


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a saved RLM slice with a verification preamble.")
    parser.add_argument("--prompt", required=True, help="Path to the saved rlm_prompt_<tag>.txt (or any prompt file).")
    parser.add_argument("--cmd-template", required=True, help="Shell command template. Vars: {model}, {slice_path}, {prompt_path}, {approval_flags}.")
    parser.add_argument("--model", default="gpt-4o", help="Model identifier for the CLI tool.")
    parser.add_argument("--timeout", type=int, default=None, help="Optional timeout seconds for the subcall.")
    parser.add_argument("--approval-flags", default="", help="Flags to control CLI approvals/sandbox.")
    parser.add_argument("--with-network", action="store_true", help="If set, add network access flags when supported.")
    parser.add_argument("--verify-prefix", default="Verification pass: ensure claims are supported and flag uncertainty.\n\n", help="Preamble added before the original prompt.")
    parser.add_argument("--output", help="Optional path to write the verification output.")
    args = parser.parse_args()

    prompt_path = Path(args.prompt)
    if not prompt_path.is_file():
        raise SystemExit(f"Prompt file not found: {prompt_path}")

    text = prompt_path.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=prompt_path.suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(args.verify_prefix + text)

    rc, out = run_subcall(args.cmd_template, args.model, tmp_path, args.timeout, args.approval_flags, args.with_network)
    if args.output:
        Path(args.output).write_text(out or "", encoding="utf-8")
    print(out)
    if rc != 0:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
