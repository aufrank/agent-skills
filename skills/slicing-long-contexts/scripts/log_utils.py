#!/usr/bin/env python
"""
Append-only logging helpers shared by rlm-cli-runner.
"""

import json
from pathlib import Path
from typing import Dict, Any


def append_log(path: Path, entry: Dict[str, Any]) -> None:
    """Append a JSON log line, creating parent dirs as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
