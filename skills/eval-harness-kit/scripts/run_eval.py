#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from grader_utils import grade_output


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_event(log_path: Path, event: str, **fields: Any) -> None:
    record = {"ts": now_iso(), "event": event, **fields}
    line = json.dumps(record, sort_keys=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def render_value(value: Any, context: dict[str, str]) -> Any:
    if isinstance(value, str):
        return value.format(**context)
    if isinstance(value, list):
        return [render_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: render_value(val, context) for key, val in value.items()}
    return value


def ensure_output(output_path: Path, stdout_text: str) -> None:
    if output_path.exists():
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(stdout_text, encoding="utf-8")


def run_command(cmd: Any, shell: bool, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=shell,
        check=False,
        text=True,
        capture_output=True,
    )


def run_llm_judge(cmd_template: str, context: dict[str, str]) -> dict[str, Any]:
    cmd = cmd_template.format(**context)
    result = run_command(cmd, shell=True, cwd=Path.cwd())
    stdout = result.stdout.strip()
    if result.returncode != 0:
        return {"passed": False, "score": 0.0, "details": "llm_judge_error", "stderr": result.stderr.strip()}
    try:
        parsed = json.loads(stdout)
        return {
            "passed": bool(parsed.get("passed", False)),
            "score": float(parsed.get("score", 0.0)),
            "details": parsed.get("details", "llm_judge"),
        }
    except json.JSONDecodeError:
        return {"passed": False, "score": 0.0, "details": "llm_judge_parse_error"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval manifest with deterministic graders.")
    parser.add_argument("--manifest", required=True, help="Path to eval manifest JSON.")
    parser.add_argument("--run-id", help="Run identifier (default: timestamp).")
    parser.add_argument("--out-dir", default="eval_runs", help="Directory for eval runs.")
    parser.add_argument("--dry-run", action="store_true", help="Only print planned runs.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    progress_log = out_dir / "progress.log"
    results_path = out_dir / "results.jsonl"
    summary_path = out_dir / "summary.json"

    log_event(progress_log, "eval.run.start", run_id=run_id, manifest=str(manifest_path))

    tasks = manifest.get("tasks", [])
    results = []
    summary = {
        "run_id": run_id,
        "manifest": str(manifest_path),
        "suite_name": manifest.get("suite_name", ""),
        "total_trials": 0,
        "total_passed": 0,
        "tasks": [],
    }

    for task in tasks:
        task_id = task["id"]
        trials = int(task.get("trials", 1))
        require_exit_zero = bool(task.get("require_exit_code_zero", True))
        task_results = []
        for trial_index in range(trials):
            trial_dir = out_dir / task_id / f"trial_{trial_index + 1}"
            trial_dir.mkdir(parents=True, exist_ok=True)
            output_path = Path(task.get("output_path", trial_dir / "output.txt"))
            transcript_path = Path(task.get("transcript_path", trial_dir / "transcript.txt"))
            stdout_path = trial_dir / "stdout.txt"
            stderr_path = trial_dir / "stderr.txt"

            context = {
                "input_path": str(task.get("input_path", "")),
                "expected_path": str(task.get("expected_path", "")),
                "output_path": str(output_path),
                "transcript_path": str(transcript_path),
                "trial_dir": str(trial_dir),
                "task_id": task_id,
                "run_id": run_id,
            }

            cmd = render_value(task.get("run_cmd", []), context)
            shell = bool(task.get("shell", False))
            if args.dry_run:
                log_event(progress_log, "eval.trial.dry_run", task_id=task_id, trial=trial_index + 1, cmd=cmd)
                continue

            start = time.time()
            result = run_command(cmd, shell=shell, cwd=Path.cwd())
            end = time.time()

            stdout_path.write_text(result.stdout, encoding="utf-8")
            stderr_path.write_text(result.stderr, encoding="utf-8")
            ensure_output(output_path, result.stdout)

            expected_path = task.get("expected_path")
            grader_results = []
            passed = True
            for grader in task.get("graders", []):
                grader_type = grader.get("type")
                if grader_type == "llm_rubric":
                    cmd_template = grader.get("judge_cmd") or manifest.get("llm_judge_cmd")
                    if not cmd_template:
                        raise ValueError("llm_rubric requires judge_cmd or manifest llm_judge_cmd")
                    llm_grade = run_llm_judge(cmd_template, context)
                    grader_results.append(
                        {
                            "type": grader_type,
                            "passed": llm_grade["passed"],
                            "score": llm_grade["score"],
                            "details": llm_grade["details"],
                        }
                    )
                    if not llm_grade["passed"]:
                        passed = False
                    continue

                grade = grade_output(
                    output_path=output_path,
                    expected_path=Path(expected_path) if expected_path else None,
                    grader=grader,
                )
                grader_results.append(
                    {
                        "type": grader_type,
                        "passed": grade.passed,
                        "score": grade.score,
                        "details": grade.details,
                    }
                )
                if not grade.passed:
                    passed = False

            if require_exit_zero and result.returncode != 0:
                passed = False

            metrics = {
                "latency_ms": int((end - start) * 1000),
                "exit_code": result.returncode,
                "stdout_bytes": stdout_path.stat().st_size,
                "stderr_bytes": stderr_path.stat().st_size,
                "output_bytes": output_path.stat().st_size if output_path.exists() else 0,
                "transcript_bytes": transcript_path.stat().st_size if transcript_path.exists() else 0,
            }

            record = {
                "run_id": run_id,
                "task_id": task_id,
                "trial": trial_index + 1,
                "passed": passed,
                "metrics": metrics,
                "graders": grader_results,
                "paths": {
                    "output": str(output_path),
                    "transcript": str(transcript_path),
                    "stdout": str(stdout_path),
                    "stderr": str(stderr_path),
                },
            }

            results.append(record)
            task_results.append(record)
            summary["total_trials"] += 1
            summary["total_passed"] += 1 if passed else 0

            with results_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")

            log_event(progress_log, "eval.trial.complete", task_id=task_id, trial=trial_index + 1, passed=passed)

        if task_results:
            task_pass = any(r["passed"] for r in task_results)
            summary["tasks"].append(
                {
                    "task_id": task_id,
                    "trials": len(task_results),
                    "passed": task_pass,
                }
            )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log_event(progress_log, "eval.run.complete", run_id=run_id, summary=str(summary_path))


if __name__ == "__main__":
    main()
