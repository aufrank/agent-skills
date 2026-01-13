#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Example agent harness stub.")
    parser.add_argument("--task", required=True, help="Task input path.")
    parser.add_argument("--output", required=True, help="Output path.")
    parser.add_argument("--transcript", required=True, help="Transcript path.")
    args = parser.parse_args()

    task_text = Path(args.task).read_text(encoding="utf-8")
    output_path = Path(args.output)
    transcript_path = Path(args.transcript)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(f"SERVER_READY\n{task_text}\n", encoding="utf-8")
    transcript_path.write_text("tool_calls=0\nturns=1\n", encoding="utf-8")


if __name__ == "__main__":
    main()
