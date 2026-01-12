#!/usr/bin/env python
"""
Subcall runner for RLM slices.
"""

import argparse
import os
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def run_subcall(
    cmd_template: str,
    model: str,
    question: str,
    prompt_path: Path,
    dry_run: bool,
    timeout: Optional[int],
    approval_flags: str,
    with_network: bool,
    extra_env: Optional[dict],
) -> Tuple[int, str]:
    cmd = cmd_template.format(
        model=model,
        question=question,
        slice_path=prompt_path,
        prompt_path=prompt_path,
        approval_flags=approval_flags.strip(),
    )
    if with_network:
        if "gemini " in cmd and "--network-access" not in cmd:
            cmd = cmd.replace("gemini ", "gemini --network-access enabled ", 1)
        if "codex " in cmd and "network_access=true" not in cmd:
            cmd = cmd.replace(
                "codex ",
                "codex -c sandbox_workspace_write.network_access=true ",
                1,
            )
    if timeout:
        cmd = f"timeout {timeout}s {cmd}"
    if dry_run:
        return 0, f"[dry-run] {cmd}"
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return res.returncode, res.stdout if res.stdout else res.stderr


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single subcall on a saved prompt.")
    parser.add_argument("--prompt", required=True, help="Path to prompt/slice file.")
    parser.add_argument("--cmd-template", required=True, help="Shell command template. Vars: {model}, {slice_path}, {prompt_path}, {approval_flags}.")
    parser.add_argument("--model", default="gpt-4o", help="Model identifier.")
    parser.add_argument("--question", default="", help="Optional root question context.")
    parser.add_argument("--approval-flags", default="", help="Approval/sandbox flags.")
    parser.add_argument("--with-network", action="store_true", help="Add network flags where supported.")
    parser.add_argument("--timeout", type=int, default=None, help="Optional timeout seconds.")
    parser.add_argument("--retry-count", type=int, default=0, help="Number of retries on nonzero return.")
    parser.add_argument("--retry-wait", type=float, default=0, help="Seconds to wait between retries.")
    parser.add_argument("--skip-on-failure", action="store_true", help="If set, exit 0 and print output even on final failure.")
    parser.add_argument("--dry-run", action="store_true", help="Print the command only.")
    parser.add_argument("--extra-env", help="Optional JSON file with env overrides (whitelisted keys only).")
    parser.add_argument("--output", help="Optional path to write output.")
    args = parser.parse_args()

    extra_env = {}
    if args.extra_env:
        extra_env = json.loads(Path(args.extra_env).read_text(encoding="utf-8"))

    attempts = 0
    rc, out = run_subcall(
        args.cmd_template,
        args.model,
        args.question,
        Path(args.prompt),
        args.dry_run,
        args.timeout,
        args.approval_flags,
        args.with_network,
        extra_env,
    )
    while rc != 0 and attempts < args.retry_count:
        attempts += 1
        if args.retry_wait:
            time.sleep(args.retry_wait)
        rc, out = run_subcall(
            args.cmd_template,
            args.model,
            args.question,
            Path(args.prompt),
            args.dry_run,
            args.timeout,
            args.approval_flags,
            args.with_network,
            extra_env,
        )

    if args.output:
        Path(args.output).write_text(out or "", encoding="utf-8")
    print(out)
    if rc != 0 and not args.skip_on_failure:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
