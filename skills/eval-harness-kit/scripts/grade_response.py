#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from grader_utils import grade_output


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade a single output against expected data.")
    parser.add_argument("--output", required=True, help="Path to output file.")
    parser.add_argument("--expected", help="Path to expected file.")
    parser.add_argument("--grader-json", help="Inline JSON grader config.")
    parser.add_argument("--grader-file", help="Path to grader JSON file.")
    args = parser.parse_args()

    if not args.grader_json and not args.grader_file:
        raise SystemExit("Provide --grader-json or --grader-file.")

    if args.grader_json:
        grader = json.loads(args.grader_json)
    else:
        grader = json.loads(Path(args.grader_file).read_text(encoding="utf-8"))

    output_path = Path(args.output)
    expected_path = Path(args.expected) if args.expected else None
    grade = grade_output(output_path, expected_path, grader)
    result = {
        "passed": grade.passed,
        "score": grade.score,
        "details": grade.details,
        "grader": grader,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
