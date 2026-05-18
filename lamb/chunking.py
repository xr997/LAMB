"""Long-document chunking utilities."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .models import TextChunk


def estimate_tokens(text: str) -> int:
    """A conservative token estimate that works well enough for planning."""

    if not text:
        return 0
    ascii_chars = sum(1 for char in text if ord(char) < 128)
    non_ascii_chars = len(text) - ascii_chars
    return max(1, ascii_chars // 4 + non_ascii_chars // 2)


def split_text(
    text: str,
    source_path: str,
    max_chars: int = 12000,
    overlap_chars: int = 800,
) -> List[TextChunk]:
    """Split text into overlapping chunks without cutting every paragraph blindly."""

    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must not be negative")
    if overlap_chars >= max_chars:
        overlap_chars = max(0, max_chars // 10)

    normalized = text.strip()
    if not normalized:
        return []

    source_name = Path(source_path).name
    if len(normalized) <= max_chars:
        return [
            TextChunk(
                source_path=source_path,
                source_name=source_name,
                index=0,
                total=1,
                text=normalized,
                start_char=0,
                end_char=len(normalized),
            )
        ]

    ranges: List[tuple[int, int]] = []
    start = 0
    while start < len(normalized):
        hard_end = min(len(normalized), start + max_chars)
        end = _best_break(normalized, start, hard_end)
        if end <= start:
            end = hard_end
        ranges.append((start, end))
        if end >= len(normalized):
            break
        next_start = max(0, end - overlap_chars)
        if next_start <= start:
            next_start = end
        start = next_start

    total = len(ranges)
    chunks = []
    for index, (start_char, end_char) in enumerate(ranges):
        chunk_text = normalized[start_char:end_char].strip()
        if not chunk_text:
            continue
        chunks.append(
            TextChunk(
                source_path=source_path,
                source_name=source_name,
                index=index,
                total=total,
                text=chunk_text,
                start_char=start_char,
                end_char=end_char,
            )
        )
    return chunks


def _best_break(text: str, start: int, hard_end: int) -> int:
    if hard_end >= len(text):
        return len(text)
    search_start = max(start, hard_end - 1600)
    window = text[search_start:hard_end]
    break_candidates = [
        window.rfind("\n\n"),
        window.rfind("\n"),
        window.rfind("。"),
        window.rfind(". "),
        window.rfind("; "),
        window.rfind("；"),
    ]
    best = max(break_candidates)
    if best <= 0:
        return hard_end
    return search_start + best + 1
