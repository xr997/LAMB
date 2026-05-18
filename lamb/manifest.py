"""Run manifest creation for auditability and repeatability."""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import DocumentRecord, RunManifest


def new_run_id(prefix: str = "run") -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{timestamp}-{uuid.uuid4().hex[:8]}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunTimer:
    """Small helper for human-readable elapsed time in manifests."""

    def __init__(self) -> None:
        self.started_at = utc_now()
        self._start = time.perf_counter()

    def finish(self) -> tuple[str, float]:
        finished_at = utc_now()
        elapsed = round(time.perf_counter() - self._start, 3)
        return finished_at, elapsed


def write_manifest(
    output_dir: str | Path,
    run_id: str,
    command: str,
    input_dir: str,
    model: str,
    parameters: Dict[str, Any],
    documents: Iterable[DocumentRecord],
    results: Iterable[Dict[str, Any]],
    summary: Dict[str, Any],
    started_at: str,
    finished_at: str,
) -> str:
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{run_id}_manifest.json"
    manifest = RunManifest(
        run_id=run_id,
        command=command,
        input_dir=str(Path(input_dir).expanduser()),
        output_dir=str(target_dir),
        started_at=started_at,
        finished_at=finished_at,
        model=model,
        parameters=parameters,
        documents=[document.to_dict() for document in documents],
        results=list(results),
        summary=summary,
    )
    target.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(target)


def compact_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    succeeded = sum(1 for result in results if result.get("success"))
    skipped = sum(1 for result in results if result.get("metadata", {}).get("skipped"))
    failed = total - succeeded - skipped
    return {
        "total": total,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
    }
