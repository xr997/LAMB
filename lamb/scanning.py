"""Directory scanning with safe defaults."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, List

from .models import DocumentRecord
from .parsing import is_supported_extension
from .security import ensure_within_directory, resolve_safe_path, should_skip_path


def scan_documents(
    input_dir: str,
    include_hidden: bool = False,
    max_file_size_mb: int = 50,
    compute_hash: bool = False,
) -> List[DocumentRecord]:
    """Scan a directory and return supported and skipped document records."""

    root = resolve_safe_path(input_dir)
    if not root.exists():
        raise FileNotFoundError(f"input directory does not exist: {input_dir}")
    if not root.is_dir():
        raise NotADirectoryError(f"input path is not a directory: {input_dir}")

    max_bytes = max_file_size_mb * 1024 * 1024
    records: List[DocumentRecord] = []
    for candidate in _walk_files(root):
        relative_path = candidate.relative_to(root)
        relative = str(relative_path)
        extension = candidate.suffix.lower()
        supported = is_supported_extension(extension)
        if candidate.is_symlink():
            records.append(
                DocumentRecord(
                    path=str(candidate),
                    relative_path=relative,
                    extension=extension,
                    size_bytes=candidate.lstat().st_size,
                    supported=supported,
                    skipped=True,
                    skip_reason="symbolic links are skipped to avoid reading outside the requested tree",
                )
            )
            continue
        ensure_within_directory(candidate, root)
        skip_reason = should_skip_path(relative_path, include_hidden=include_hidden)
        size_bytes = candidate.stat().st_size
        if size_bytes > max_bytes:
            skip_reason = f"file exceeds size limit: {max_file_size_mb} MB"
        if not supported and not skip_reason:
            skip_reason = f"unsupported extension: {extension or '<none>'}"
        sha256 = _hash_file(candidate) if compute_hash and supported and not skip_reason else None
        records.append(
            DocumentRecord(
                path=str(candidate),
                relative_path=relative,
                extension=extension,
                size_bytes=size_bytes,
                supported=supported,
                skipped=bool(skip_reason),
                skip_reason=skip_reason,
                sha256=sha256,
            )
        )
    return sorted(records, key=lambda record: record.relative_path)


def supported_records(records: Iterable[DocumentRecord]) -> List[DocumentRecord]:
    return [record for record in records if record.supported and not record.skipped]


def summarize_scan(records: Iterable[DocumentRecord]) -> dict[str, int]:
    records_list = list(records)
    return {
        "total": len(records_list),
        "supported": sum(1 for record in records_list if record.supported and not record.skipped),
        "skipped": sum(1 for record in records_list if record.skipped),
        "unsupported": sum(1 for record in records_list if not record.supported and not record.skipped),
    }


def _walk_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def _hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
