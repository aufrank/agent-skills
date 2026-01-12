#!/usr/bin/env python
"""
Slice helpers for RLM runs.
"""

import re
import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence


@dataclass
class Slice:
    tag: str
    path: Path
    start: int
    end: int
    text: str


def slice_prompt(
    prompt: str,
    chunk_size: int,
    marker_start: Optional[str],
    marker_end: Optional[str],
    max_slices: int,
    prefer_headings: bool = False,
    overlap: int = 0,
    base_dir: Optional[Path] = None,
) -> List[Slice]:
    slices: List[Slice] = []
    base_dir = base_dir or Path(".")
    base_dir.mkdir(parents=True, exist_ok=True)
    if prefer_headings:
        heading_matches = list(re.finditer(r"(?m)^#{1,6}\s+.+$", prompt))
        boundaries = [0] + [m.start() for m in heading_matches] + [len(prompt)]
        sections: list[Slice] = []
        for idx in range(len(boundaries) - 1):
            start, end = boundaries[idx], boundaries[idx + 1]
            text = prompt[start:end]
            if not text.strip():
                continue
            sections.append(Slice(tag=f"sec{idx}", path=base_dir / f"tmp_sec_{idx}.txt", start=start, end=end, text=text))

        chunks: list[Slice] = []
        current_parts: list[Slice] = []
        current_len = 0

        for sec in sections:
            sec_len = len(sec.text)
            if current_parts and current_len + sec_len > chunk_size and len(chunks) < max_slices - 1:
                start = current_parts[0].start
                end = current_parts[-1].end
                text = "".join(part.text for part in current_parts)
                tag = f"h{len(chunks)}"
                chunks.append(Slice(tag=tag, path=base_dir / f"rlm_slice_{tag}.txt", start=start, end=end, text=text))
                current_parts = []
                current_len = 0

            current_parts.append(sec)
            current_len += sec_len

            if sec_len >= chunk_size and len(current_parts) == 1 and len(chunks) < max_slices:
                start, end = sec.start, sec.end
                tag = f"h{len(chunks)}"
                chunks.append(Slice(tag=tag, path=base_dir / f"rlm_slice_{tag}.txt", start=start, end=end, text=sec.text))
                current_parts = []
                current_len = 0

        if current_parts and len(chunks) < max_slices:
            start = current_parts[0].start
            end = current_parts[-1].end
            text = "".join(part.text for part in current_parts)
            tag = f"h{len(chunks)}"
            chunks.append(Slice(tag=tag, path=base_dir / f"rlm_slice_{tag}.txt", start=start, end=end, text=text))

        slices.extend(chunks[:max_slices])
    if marker_start:
        pattern_start = re.compile(marker_start)
        pattern_end = re.compile(marker_end) if marker_end else None
        for idx, match in enumerate(pattern_start.finditer(prompt)):
            start = match.start()
            if pattern_end:
                next_match = pattern_end.search(prompt, match.end())
                end = next_match.start() if next_match else len(prompt)
            else:
                end = len(prompt)
            text = prompt[start:end]
            tag = f"m{idx}"
            slices.append(Slice(tag=tag, path=base_dir / f"rlm_slice_{tag}.txt", start=start, end=end, text=text))
            if len(slices) >= max_slices:
                break
    if not slices:
        step = max(chunk_size - max(overlap, 0), 1)
        for i in range(0, len(prompt), step):
            tag = f"c{i//chunk_size}"
            start, end = i, min(i + chunk_size, len(prompt))
            text = prompt[start:end]
            slices.append(Slice(tag=tag, path=base_dir / f"rlm_slice_{tag}.txt", start=start, end=end, text=text))
            if len(slices) >= max_slices:
                break
    return slices


def write_slices(slices: Sequence[Slice]) -> None:
    for s in slices:
        s.path.write_text(s.text, encoding="utf-8")


def write_manifest(slices: Sequence[Slice], manifest_path: Path) -> None:
    manifest = [
        {"tag": s.tag, "path": str(s.path), "start": s.start, "end": s.end, "len": len(s.text)}
        for s in slices
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def load_manifest(manifest_path: Path) -> List[Slice]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    slices: List[Slice] = []
    for entry in data:
        slices.append(
            Slice(
                tag=entry["tag"],
                path=Path(entry["path"]),
                start=entry["start"],
                end=entry["end"],
                text="",
            )
        )
    return slices


def main() -> None:
    parser = argparse.ArgumentParser(description="Slice a prompt into heading/marker/chunk-based slices.")
    parser.add_argument("--prompt", required=True, help="Path to the prompt file.")
    parser.add_argument("--chunk-size", type=int, default=200_000, help="Chunk size when no markers are provided.")
    parser.add_argument("--overlap", type=int, default=0, help="Optional overlap (chars) for fixed-size chunking.")
    parser.add_argument("--marker-start", help="Regex for slice start (optional).")
    parser.add_argument("--marker-end", help="Regex for slice end (optional).")
    parser.add_argument("--max-slices", type=int, default=5, help="Max slices to emit.")
    parser.add_argument("--prefer-headings", action="store_true", help="Prefer Markdown heading-based slices.")
    parser.add_argument("--out-dir", default=".", help="Output directory for slices/manifest.")
    parser.add_argument("--manifest", default=None, help="Manifest path (defaults to <out-dir>/manifest.json).")
    args = parser.parse_args()

    prompt_path = Path(args.prompt)
    if not prompt_path.is_file():
        raise SystemExit(f"Prompt file not found: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    slices = slice_prompt(
        prompt,
        args.chunk_size,
        args.marker_start,
        args.marker_end,
        args.max_slices,
        prefer_headings=args.prefer_headings,
        overlap=args.overlap,
        base_dir=out_dir,
    )
    write_slices(slices)
    manifest_path = Path(args.manifest) if args.manifest else out_dir / "manifest.json"
    write_manifest(slices, manifest_path)
    print(f"Wrote {len(slices)} slices and manifest to {manifest_path}")


if __name__ == "__main__":
    main()
