#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass
class GradeResult:
    passed: bool
    score: float
    details: str


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_contains(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        for key, value in expected.items():
            if key not in actual:
                return False
            if not _json_contains(actual[key], value):
                return False
        return True
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        return all(any(_json_contains(item, needle) for item in actual) for needle in expected)
    return actual == expected


def grade_exact(output_text: str, expected_text: str, strip: bool) -> GradeResult:
    if strip:
        output_text = output_text.strip()
        expected_text = expected_text.strip()
    passed = output_text == expected_text
    return GradeResult(passed, 1.0 if passed else 0.0, "exact_match")


def grade_contains(output_text: str, needle: str) -> GradeResult:
    passed = needle in output_text
    return GradeResult(passed, 1.0 if passed else 0.0, "contains")


def grade_regex(output_text: str, pattern: str, flags: Iterable[str]) -> GradeResult:
    flag_value = 0
    for flag in flags:
        if flag.lower() == "i":
            flag_value |= re.IGNORECASE
        if flag.lower() == "m":
            flag_value |= re.MULTILINE
        if flag.lower() == "s":
            flag_value |= re.DOTALL
    passed = re.search(pattern, output_text, flags=flag_value) is not None
    return GradeResult(passed, 1.0 if passed else 0.0, "regex")


def grade_json_contains(actual: Any, expected: Any) -> GradeResult:
    passed = _json_contains(actual, expected)
    return GradeResult(passed, 1.0 if passed else 0.0, "json_contains")


def grade_json_equal(actual: Any, expected: Any) -> GradeResult:
    passed = actual == expected
    return GradeResult(passed, 1.0 if passed else 0.0, "json_equal")


def grade_exists(path: Path) -> GradeResult:
    passed = path.exists() and path.stat().st_size > 0
    return GradeResult(passed, 1.0 if passed else 0.0, "exists")


def grade_output(output_path: Path, expected_path: Path | None, grader: dict[str, Any]) -> GradeResult:
    grader_type = grader.get("type", "").strip()
    if grader_type == "exists":
        return grade_exists(output_path)

    output_text = load_text(output_path) if output_path.exists() else ""

    if grader_type == "exact_match":
        if expected_path is None:
            raise ValueError("exact_match requires expected_path")
        expected_text = load_text(expected_path)
        return grade_exact(output_text, expected_text, bool(grader.get("strip", True)))

    if grader_type == "contains":
        return grade_contains(output_text, str(grader.get("needle", "")))

    if grader_type == "regex":
        pattern = str(grader.get("pattern", ""))
        flags = grader.get("flags", [])
        if not isinstance(flags, list):
            flags = [flags]
        return grade_regex(output_text, pattern, flags)

    if grader_type in {"json_contains", "json_equal"}:
        if expected_path is None:
            raise ValueError(f"{grader_type} requires expected_path")
        actual_json = load_json(output_path)
        expected_json = load_json(expected_path)
        if grader_type == "json_contains":
            return grade_json_contains(actual_json, expected_json)
        return grade_json_equal(actual_json, expected_json)

    raise ValueError(f"Unknown grader type: {grader_type}")
