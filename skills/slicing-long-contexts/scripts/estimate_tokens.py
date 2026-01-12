#!/usr/bin/env python
"""
Estimate tokens for one or more files.
"""

import argparse
from pathlib import Path

from token_utils import estimate_tokens


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate tokens for files (heuristic, optional tiktoken).")
    parser.add_argument("files", nargs="+", help="Paths to text/markdown files.")
    parser.add_argument("--model", help="Optional model name for tiktoken encoding.")
    args = parser.parse_args()

    total_chars = 0
    total_tokens = 0
    for f in args.files:
        path = Path(f)
        if not path.is_file():
            print(f"{f}: not found")
            continue
        text = path.read_text(encoding="utf-8")
        chars = len(text)
        toks = estimate_tokens(text, model=args.model)
        total_chars += chars
        total_tokens += toks
        print(f"{f}: chars={chars}, est_tokens={toks}")
    if len(args.files) > 1:
        print(f"TOTAL: chars={total_chars}, est_tokens={total_tokens}")


if __name__ == "__main__":
    main()
