"""Output writers for LAMB reports and extracted data."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


def ensure_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_stem(name: str, fallback: str = "document") -> str:
    stem = Path(name).stem or fallback
    cleaned = re.sub(r"[^\w.\-\u4e00-\u9fff]+", "_", stem, flags=re.UNICODE).strip("._")
    return cleaned or fallback


def write_text(content: str, path: str | Path) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


def write_json(data: Any, path: str | Path) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(target)


def write_csv(rows: Sequence[Mapping[str, Any]], path: str | Path, fields: Sequence[str] | None = None) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = list(fields or _union_headers(rows))
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: _stringify(row.get(header, "")) for header in headers})
    return str(target)


def write_docx(content: str, path: str | Path) -> str:
    try:
        import docx
    except ImportError as exc:
        raise RuntimeError("python-docx is required to write .docx output") from exc

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    document = docx.Document()
    for line in content.splitlines() or [""]:
        document.add_paragraph(line)
    document.save(str(target))
    return str(target)


def write_content(content: str, path: str | Path, output_format: str = "md") -> str:
    format_name = output_format.lower().lstrip(".")
    target = Path(path)
    if format_name in {"txt", "md", "markdown"}:
        return write_text(content, target)
    if format_name == "docx":
        return write_docx(content, target)
    raise ValueError(f"unsupported text output format: {output_format}")


def _union_headers(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    headers: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in headers:
                headers.append(key)
    return headers


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
