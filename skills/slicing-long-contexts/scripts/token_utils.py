#!/usr/bin/env python
"""
Token estimation helpers.
"""

from __future__ import annotations

import math
from typing import Optional


def estimate_tokens(text: str, model: Optional[str] = None) -> int:
    """
    Estimate token count for text. If tiktoken is available, use it; otherwise
    use a simple heuristic (~4 chars per token).
    """
    try:
        import tiktoken  # type: ignore

        enc = tiktoken.encoding_for_model(model) if model else tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return math.ceil(len(text) / 4)
