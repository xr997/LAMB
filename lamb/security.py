"""Application-layer safety helpers for LLM document processing."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import SecurityFinding


DEFAULT_DENY_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials",
    "credentials.json",
    "secrets.json",
}


@dataclass(frozen=True)
class InjectionRule:
    """A single prompt-injection detection rule."""

    rule_id: str
    severity: str
    message: str
    pattern: re.Pattern[str]


def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE)


DEFAULT_INJECTION_RULES: Sequence[InjectionRule] = (
    InjectionRule(
        "ignore-instructions",
        "high",
        "Document appears to ask the model to ignore prior instructions.",
        _compile(r"\b(ignore|disregard|forget|override)\b.{0,80}\b(previous|prior|above|system|developer)\b.{0,40}\binstruction"),
    ),
    InjectionRule(
        "system-prompt-exfiltration",
        "high",
        "Document appears to request hidden system or developer prompts.",
        _compile(r"\b(reveal|print|show|dump|exfiltrate)\b.{0,80}\b(system prompt|developer message|hidden prompt|initial prompt)"),
    ),
    InjectionRule(
        "tool-abuse",
        "medium",
        "Document appears to instruct the agent to call tools or execute commands.",
        _compile(r"\b(call|invoke|use|execute|run)\b.{0,80}\b(tool|function|shell|command|terminal|python|bash|powershell)"),
    ),
    InjectionRule(
        "secret-access",
        "high",
        "Document appears to request secrets, API keys, environment variables, or tokens.",
        _compile(r"\b(read|open|print|send|upload|leak|steal)\b.{0,80}\b(api[_ -]?key|token|secret|password|\.env|environment variable)"),
    ),
    InjectionRule(
        "role-play-jailbreak",
        "medium",
        "Document contains common jailbreak or role override language.",
        _compile(r"\b(you are now|act as|developer mode|do anything now|jailbreak|unfiltered)\b"),
    ),
)


SECRET_PATTERNS: Sequence[tuple[str, re.Pattern[str]]] = (
    ("openai_key", _compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("generic_api_key", _compile(r"\b(api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}")),
    ("jwt", _compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")),
    ("email", _compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")),
    ("phone_cn", _compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("phone_intl", _compile(r"\+\d{1,3}[\s-]?(?:\d[\s-]?){7,14}\d")),
)


class PromptInjectionDetector:
    """Detect prompt-injection and tool-abuse instructions in document text."""

    def __init__(self, rules: Sequence[InjectionRule] = DEFAULT_INJECTION_RULES):
        self.rules = list(rules)

    def inspect(self, text: str, max_findings: int = 20) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        for rule in self.rules:
            for match in rule.pattern.finditer(text):
                findings.append(
                    SecurityFinding(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=rule.message,
                        snippet=_compact_snippet(text, match.start(), match.end()),
                    )
                )
                if len(findings) >= max_findings:
                    return findings
        return findings

    def highest_severity(self, findings: Iterable[SecurityFinding]) -> str:
        order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        highest = "low"
        for finding in findings:
            if order.get(finding.severity, 0) > order.get(highest, 0):
                highest = finding.severity
        return highest


class SensitiveDataRedactor:
    """Mask common personal data and token-like strings before sending text to an LLM."""

    def __init__(self, patterns: Sequence[tuple[str, re.Pattern[str]]] = SECRET_PATTERNS):
        self.patterns = list(patterns)

    def redact(self, text: str) -> tuple[str, List[SecurityFinding]]:
        findings: List[SecurityFinding] = []
        redacted = text
        for label, pattern in self.patterns:
            matches = list(pattern.finditer(redacted))
            if not matches:
                continue
            redacted = pattern.sub(f"[REDACTED:{label}]", redacted)
            findings.append(
                SecurityFinding(
                    rule_id=f"redacted-{label}",
                    severity="low",
                    message=f"Sensitive-looking {label} value was redacted before LLM processing.",
                    snippet=f"{len(matches)} occurrence(s)",
                )
            )
        return redacted, findings


def should_skip_path(path: Path, include_hidden: bool = False) -> str:
    """Return a skip reason for paths that should not be ingested."""

    name = path.name
    lower = name.lower()
    if lower in DEFAULT_DENY_NAMES:
        return f"refusing to read sensitive file name: {name}"
    if not include_hidden and any(part.startswith(".") for part in path.parts):
        return "hidden files are skipped by default"
    if path.is_symlink():
        return "symbolic links are skipped to avoid reading outside the requested tree"
    return ""


def resolve_safe_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve()


def ensure_within_directory(candidate: Path, root: Path) -> None:
    """Raise ValueError if candidate escapes root."""

    candidate_resolved = candidate.expanduser().resolve()
    root_resolved = root.expanduser().resolve()
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"path escapes input directory: {candidate}") from exc


def has_high_risk_findings(findings: Iterable[SecurityFinding]) -> bool:
    return any(finding.severity in {"high", "critical"} for finding in findings)


def format_findings(findings: Iterable[SecurityFinding]) -> str:
    parts = []
    for finding in findings:
        snippet = f" ({finding.snippet})" if finding.snippet else ""
        parts.append(f"{finding.severity}:{finding.rule_id}{snippet}")
    return "; ".join(parts)


def _compact_snippet(text: str, start: int, end: int, radius: int = 60) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = text[left:right].replace("\n", " ").strip()
    return re.sub(r"\s+", " ", snippet)
