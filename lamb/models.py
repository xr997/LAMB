"""Typed result objects used by the public LAMB SDK."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SecurityFinding:
    """A risk signal found while inspecting user-controlled document content."""

    rule_id: str
    severity: str
    message: str
    snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentRecord:
    """A file discovered during a directory scan."""

    path: str
    relative_path: str
    extension: str
    size_bytes: int
    supported: bool
    skipped: bool = False
    skip_reason: str = ""
    sha256: Optional[str] = None
    findings: List[SecurityFinding] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return self.relative_path or Path(self.path).name

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [finding.to_dict() for finding in self.findings]
        return data


@dataclass
class TextChunk:
    """A bounded section of parsed document text."""

    source_path: str
    source_name: str
    index: int
    total: int
    text: str
    start_char: int
    end_char: int

    @property
    def label(self) -> str:
        return f"{self.source_name}#chunk-{self.index + 1}-of-{self.total}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileResult:
    """Result for a single input document."""

    input_path: str
    output_path: Optional[str]
    success: bool
    message: str
    findings: List[SecurityFinding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [finding.to_dict() for finding in self.findings]
        return data


@dataclass
class BatchResult:
    """Result for directory-level batch processing."""

    run_id: str
    input_dir: str
    output_dir: str
    total: int
    succeeded: int
    failed: int
    skipped: int
    files: List[FileResult]
    manifest_path: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.failed == 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["files"] = [result.to_dict() for result in self.files]
        return data


@dataclass
class QAResult:
    """Result for cross-document research and question answering."""

    run_id: str
    question: str
    answer: str
    report_path: Optional[str]
    manifest_path: Optional[str]
    sources: List[str]
    findings: List[SecurityFinding] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    failed: int = 0

    @property
    def ok(self) -> bool:
        return bool(self.answer) and self.failed == 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [finding.to_dict() for finding in self.findings]
        return data


@dataclass
class ExtractionResult:
    """Result for structured field extraction over a directory."""

    run_id: str
    fields: List[str]
    rows: List[Dict[str, Any]]
    output_path: Optional[str]
    manifest_path: Optional[str]
    files: List[FileResult]

    @property
    def ok(self) -> bool:
        return all(result.success for result in self.files if not result.metadata.get("skipped"))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["files"] = [result.to_dict() for result in self.files]
        return data


@dataclass
class RunManifest:
    """Serializable audit record for a LAMB run."""

    run_id: str
    command: str
    input_dir: str
    output_dir: str
    started_at: str
    finished_at: str
    model: str
    parameters: Dict[str, Any]
    documents: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
