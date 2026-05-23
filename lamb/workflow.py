"""Public LAMB workflows for CLI and third-party programs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .chunking import estimate_tokens, split_text
from .llm import DryRunClient, LLMClient, OpenAIChatClient
from .manifest import RunTimer, compact_summary, new_run_id, write_manifest
from .models import BatchResult, DocumentRecord, ExtractionResult, FileResult, QAResult, SecurityFinding, TextChunk
from .parsing import ParseError, is_supported_extension, parse_document
from .prompts import (
    build_batch_reduce_prompt,
    build_extraction_prompt,
    build_mapping_prompt,
    build_research_map_prompt,
    build_research_reduce_prompt,
)
from .scanning import scan_documents
from .security import PromptInjectionDetector, SensitiveDataRedactor, format_findings, has_high_risk_findings
from .writers import ensure_output_dir, safe_stem, write_content, write_csv, write_json, write_output_index, write_text


@dataclass
class PreparedDocument:
    text: str
    findings: List[SecurityFinding]
    chunks: List[TextChunk]
    tokens_estimate: int


def process_file(
    file_path: str,
    instruction: str,
    output_dir: str = "data/outputs",
    output_format: str = "docx",
    llm_client: LLMClient | None = None,
    model_name: str | None = None,
    dry_run: bool = False,
    strict_security: bool = False,
    redact: bool = False,
    max_chars: int = 12000,
) -> FileResult:
    """Process one file and write one output artifact."""

    path = Path(file_path).expanduser().resolve()
    record = DocumentRecord(
        path=str(path),
        relative_path=path.name,
        extension=path.suffix.lower(),
        size_bytes=path.stat().st_size if path.exists() else 0,
        supported=is_supported_extension(path.suffix.lower()),
    )
    if not record.supported:
        return FileResult(
            input_path=str(path),
            output_path=None,
            success=False,
            message=f"unsupported extension: {record.extension or '<none>'}",
            metadata={"skipped": True},
        )
    client = _resolve_client(llm_client, dry_run, model_name)
    output_root = ensure_output_dir(output_dir)
    return _process_record_mapping(
        record=record,
        instruction=instruction,
        output_dir=output_root,
        output_format=output_format,
        client=client,
        strict_security=strict_security,
        redact=redact,
        max_chars=max_chars,
    )


def process_directory(
    input_dir: str,
    instruction: str,
    mode: str = "mapping",
    output_dir: str = "data/outputs",
    output_format: str = "docx",
    dry_run: bool = False,
    strict_security: bool = False,
    redact: bool = False,
    llm_client: LLMClient | None = None,
    model_name: str | None = None,
    max_chars: int = 12000,
    include_hidden: bool = False,
) -> BatchResult:
    """Process a directory in mapping or aggregation mode."""

    normalized_mode = mode.lower()
    if normalized_mode not in {"mapping", "aggregation"}:
        raise ValueError("mode must be 'mapping' or 'aggregation'")
    if normalized_mode == "aggregation":
        fields = _fields_from_instruction(instruction)
        aggregation_format = output_format.lower().lstrip(".")
        if aggregation_format not in {"csv", "json"}:
            aggregation_format = "csv"
        extraction = extract_fields(
            input_dir=input_dir,
            fields=fields,
            output_dir=output_dir,
            output_format=aggregation_format,
            dry_run=dry_run,
            strict_security=strict_security,
            redact=redact,
            llm_client=llm_client,
            model_name=model_name,
            max_chars=max_chars,
            include_hidden=include_hidden,
        )
        files = extraction.files
        succeeded = sum(1 for result in files if result.success)
        skipped = sum(1 for result in files if result.metadata.get("skipped"))
        failed = len(files) - succeeded - skipped
        return BatchResult(
            run_id=extraction.run_id,
            input_dir=input_dir,
            output_dir=output_dir,
            total=len(files),
            succeeded=succeeded,
            failed=failed,
            skipped=skipped,
            files=files,
            manifest_path=extraction.manifest_path,
        )

    run_id = new_run_id("batch")
    timer = RunTimer()
    output_root = ensure_output_dir(output_dir)
    records = scan_documents(input_dir, include_hidden=include_hidden)
    client = _resolve_client(llm_client, dry_run, model_name)
    results: List[FileResult] = []
    for record in records:
        if record.skipped or not record.supported:
            results.append(_skipped_result(record))
            continue
        result = _process_record_mapping(
            record=record,
            instruction=instruction,
            output_dir=output_root,
            output_format=output_format,
            client=client,
            strict_security=strict_security,
            redact=redact,
            max_chars=max_chars,
        )
        results.append(result)

    finished_at, elapsed = timer.finish()
    summary = compact_summary([result.to_dict() for result in results])
    summary["elapsed_seconds"] = elapsed
    manifest_path = write_manifest(
        output_dir=output_root,
        run_id=run_id,
        command="batch",
        input_dir=input_dir,
        model=client.model_name,
        parameters={
            "instruction": instruction,
            "mode": normalized_mode,
            "output_format": output_format,
            "dry_run": dry_run,
            "strict_security": strict_security,
            "redact": redact,
            "max_chars": max_chars,
            "include_hidden": include_hidden,
        },
        documents=records,
        results=[result.to_dict() for result in results],
        summary=summary,
        started_at=timer.started_at,
        finished_at=finished_at,
    )
    write_output_index(
        output_dir=output_root,
        run_id=run_id,
        command="batch",
        summary=summary,
        manifest_path=manifest_path,
        output_paths=[result.output_path for result in results],
    )
    return BatchResult(
        run_id=run_id,
        input_dir=input_dir,
        output_dir=str(output_root),
        total=len(results),
        succeeded=summary["succeeded"],
        failed=summary["failed"],
        skipped=summary["skipped"],
        files=results,
        manifest_path=manifest_path,
    )


def answer_over_directory(
    input_dir: str,
    question: str,
    output_dir: str = "data/outputs",
    dry_run: bool = False,
    strict_security: bool = False,
    redact: bool = False,
    llm_client: LLMClient | None = None,
    model_name: str | None = None,
    max_chars: int = 12000,
    include_hidden: bool = False,
) -> QAResult:
    """Answer a question over all supported documents in a directory."""

    run_id = new_run_id("research")
    timer = RunTimer()
    output_root = ensure_output_dir(output_dir)
    records = scan_documents(input_dir, include_hidden=include_hidden)
    client = _resolve_client(llm_client, dry_run, model_name)
    detector = PromptInjectionDetector()
    redactor = SensitiveDataRedactor()
    evidence_notes: List[str] = []
    sources: List[str] = []
    skipped_files: List[str] = []
    all_findings: List[SecurityFinding] = []
    file_results: List[FileResult] = []

    for record in records:
        if record.skipped or not record.supported:
            skipped_files.append(record.relative_path)
            file_results.append(_skipped_result(record))
            continue
        try:
            prepared, failure = _prepare_record(
                record=record,
                detector=detector,
                redactor=redactor,
                strict_security=strict_security,
                redact=redact,
                max_chars=max_chars,
            )
            all_findings.extend(record.findings)
            if failure:
                if failure.metadata.get("skipped"):
                    skipped_files.append(record.relative_path)
                file_results.append(failure)
                continue
            if dry_run:
                evidence_notes.append(_dry_run_evidence(record, prepared.chunks, prepared.findings))
            else:
                llm_fallbacks: List[str] = []
                for chunk in prepared.chunks:
                    prompt = build_research_map_prompt(question, chunk, prepared.findings)
                    try:
                        note = client.generate(prompt)
                    except Exception as exc:
                        llm_fallbacks.append(f"{chunk.label}: {exc}")
                        note = _fallback_evidence_note(chunk, exc)
                    if note and "NO_RELEVANT_EVIDENCE" not in note:
                        evidence_notes.append(f"### {chunk.label}\n{note}")
            sources.append(record.relative_path)
            metadata = {"chunks": len(prepared.chunks), "tokens_estimate": prepared.tokens_estimate}
            if not dry_run and llm_fallbacks:
                metadata["llm_fallbacks"] = llm_fallbacks
            file_results.append(
                FileResult(
                    input_path=record.path,
                    output_path=None,
                    success=True,
                    message=_processed_message(len(prepared.chunks), 0 if dry_run else len(llm_fallbacks)),
                    findings=prepared.findings,
                    metadata=metadata,
                )
            )
        except Exception as exc:
            file_results.append(FileResult(record.path, None, False, str(exc)))

    if dry_run:
        answer = _dry_run_research_report(question, sources, evidence_notes, skipped_files)
    elif evidence_notes:
        try:
            answer = client.generate(build_research_reduce_prompt(question, evidence_notes))
        except Exception as exc:
            answer = _fallback_research_report(question, sources, evidence_notes, skipped_files, exc)
            file_results.append(
                FileResult(
                    input_path="<research-reduce>",
                    output_path=None,
                    success=True,
                    message=f"LLM reduce stage failed; wrote fallback report: {exc}",
                    metadata={"stage": "reduce", "llm_fallback": True},
                )
            )
    else:
        answer = "未在支持的文档中找到足够证据回答该问题。"

    report_path = write_text(answer, output_root / f"{run_id}_research.md")
    finished_at, elapsed = timer.finish()
    result_dicts = [result.to_dict() for result in file_results]
    summary = compact_summary(result_dicts)
    summary["elapsed_seconds"] = elapsed
    summary["sources"] = len(sources)
    manifest_path = write_manifest(
        output_dir=output_root,
        run_id=run_id,
        command="research",
        input_dir=input_dir,
        model=client.model_name,
        parameters={
            "question": question,
            "dry_run": dry_run,
            "strict_security": strict_security,
            "redact": redact,
            "max_chars": max_chars,
            "include_hidden": include_hidden,
        },
        documents=records,
        results=result_dicts,
        summary=summary,
        started_at=timer.started_at,
        finished_at=finished_at,
    )
    write_output_index(
        output_dir=output_root,
        run_id=run_id,
        command="research",
        summary=summary,
        manifest_path=manifest_path,
        output_paths=[report_path],
    )
    return QAResult(
        run_id=run_id,
        question=question,
        answer=answer,
        report_path=report_path,
        manifest_path=manifest_path,
        sources=sources,
        findings=all_findings,
        skipped_files=skipped_files,
        failed=summary["failed"],
    )


def extract_fields(
    input_dir: str,
    fields: Sequence[str],
    output_dir: str = "data/outputs",
    output_format: str = "csv",
    dry_run: bool = False,
    strict_security: bool = False,
    redact: bool = False,
    llm_client: LLMClient | None = None,
    model_name: str | None = None,
    max_chars: int = 12000,
    include_hidden: bool = False,
) -> ExtractionResult:
    """Extract structured fields from each supported document."""

    normalized_fields = _normalize_fields(fields)
    output_format_normalized = _normalize_extraction_format(output_format)
    run_id = new_run_id("extract")
    timer = RunTimer()
    output_root = ensure_output_dir(output_dir)
    records = scan_documents(input_dir, include_hidden=include_hidden)
    client = _resolve_client(llm_client, dry_run, model_name)
    detector = PromptInjectionDetector()
    redactor = SensitiveDataRedactor()
    rows: List[Dict[str, Any]] = []
    file_results: List[FileResult] = []

    for record in records:
        if record.skipped or not record.supported:
            file_results.append(_skipped_result(record))
            continue
        try:
            prepared, failure = _prepare_record(
                record=record,
                detector=detector,
                redactor=redactor,
                strict_security=strict_security,
                redact=redact,
                max_chars=max_chars,
            )
            if failure:
                file_results.append(failure)
                continue
            row = {"source_file": record.relative_path}
            row.update({field: "" for field in normalized_fields})
            if dry_run:
                row["dry_run"] = "true"
            else:
                chunk_rows = []
                for chunk in prepared.chunks:
                    response = client.generate(build_extraction_prompt(normalized_fields, chunk, prepared.findings))
                    chunk_rows.append(_extract_json_object(response))
                row.update(_merge_extraction_rows(normalized_fields, chunk_rows))
            rows.append(row)
            file_results.append(
                FileResult(
                    input_path=record.path,
                    output_path=None,
                    success=True,
                    message=f"extracted {len(normalized_fields)} field(s)",
                    findings=prepared.findings,
                    metadata={"chunks": len(prepared.chunks)},
                )
            )
        except Exception as exc:
            file_results.append(FileResult(record.path, None, False, str(exc)))

    if output_format_normalized == "json":
        output_path = write_json(rows, output_root / f"{run_id}_extraction.json")
    else:
        output_path = write_csv(rows, output_root / f"{run_id}_extraction.csv", fields=["source_file", *normalized_fields])

    finished_at, elapsed = timer.finish()
    result_dicts = [result.to_dict() for result in file_results]
    summary = compact_summary(result_dicts)
    summary["elapsed_seconds"] = elapsed
    summary["rows"] = len(rows)
    manifest_path = write_manifest(
        output_dir=output_root,
        run_id=run_id,
        command="extract",
        input_dir=input_dir,
        model=client.model_name,
        parameters={
            "fields": normalized_fields,
            "output_format": output_format,
            "dry_run": dry_run,
            "strict_security": strict_security,
            "redact": redact,
            "max_chars": max_chars,
            "include_hidden": include_hidden,
        },
        documents=records,
        results=result_dicts,
        summary=summary,
        started_at=timer.started_at,
        finished_at=finished_at,
    )
    write_output_index(
        output_dir=output_root,
        run_id=run_id,
        command="extract",
        summary=summary,
        manifest_path=manifest_path,
        output_paths=[output_path],
    )
    return ExtractionResult(
        run_id=run_id,
        fields=normalized_fields,
        rows=rows,
        output_path=output_path,
        manifest_path=manifest_path,
        files=file_results,
    )


def _process_record_mapping(
    record: DocumentRecord,
    instruction: str,
    output_dir: Path,
    output_format: str,
    client: LLMClient,
    strict_security: bool,
    redact: bool,
    max_chars: int,
) -> FileResult:
    detector = PromptInjectionDetector()
    redactor = SensitiveDataRedactor()
    try:
        prepared, failure = _prepare_record(
            record=record,
            detector=detector,
            redactor=redactor,
            strict_security=strict_security,
            redact=redact,
            max_chars=max_chars,
        )
        if failure:
            return failure
        chunk_outputs = [
            client.generate(build_mapping_prompt(instruction, chunk, prepared.findings)) for chunk in prepared.chunks
        ]
        if len(chunk_outputs) == 1:
            final_output = chunk_outputs[0]
        else:
            final_output = client.generate(build_batch_reduce_prompt(instruction, record.relative_path, chunk_outputs))
        extension = _text_output_extension(output_format)
        output_path = output_dir / f"{safe_stem(record.relative_path)}_processed.{extension}"
        saved_path = write_content(final_output, output_path, output_format=output_format)
        return FileResult(
            input_path=record.path,
            output_path=saved_path,
            success=True,
            message=f"processed {len(prepared.chunks)} chunk(s)",
            findings=prepared.findings,
            metadata={"chunks": len(prepared.chunks), "tokens_estimate": prepared.tokens_estimate},
        )
    except (ParseError, OSError, RuntimeError, ValueError) as exc:
        return FileResult(record.path, None, False, str(exc))


def _prepare_record(
    record: DocumentRecord,
    detector: PromptInjectionDetector,
    redactor: SensitiveDataRedactor,
    strict_security: bool,
    redact: bool,
    max_chars: int,
) -> tuple[PreparedDocument | None, FileResult | None]:
    try:
        text = parse_document(record.path)
        findings = detector.inspect(text)
        if redact:
            text, redaction_findings = redactor.redact(text)
            findings.extend(redaction_findings)
        record.findings = findings
        if strict_security and has_high_risk_findings(findings):
            return None, FileResult(
                input_path=record.path,
                output_path=None,
                success=False,
                message=f"skipped by strict security policy: {format_findings(findings)}",
                findings=findings,
                metadata={"skipped": True, "security_skipped": True},
            )
        chunks = split_text(text, record.path, max_chars=max_chars)
        if not chunks:
            return None, FileResult(
                input_path=record.path,
                output_path=None,
                success=False,
                message="empty parsed document",
                findings=findings,
                metadata={"skipped": True, "empty": True},
            )
        return PreparedDocument(
            text=text,
            findings=findings,
            chunks=chunks,
            tokens_estimate=estimate_tokens(text),
        ), None
    except (ParseError, OSError, ValueError) as exc:
        return None, FileResult(
            input_path=record.path,
            output_path=None,
            success=False,
            message=str(exc),
            findings=record.findings,
        )


def _resolve_client(llm_client: LLMClient | None, dry_run: bool, model_name: str | None = None) -> LLMClient:
    if llm_client is not None:
        return llm_client
    if dry_run:
        return DryRunClient()
    return OpenAIChatClient(model_name=model_name)


def _skipped_result(record: DocumentRecord) -> FileResult:
    reason = record.skip_reason or "unsupported file"
    return FileResult(
        input_path=record.path,
        output_path=None,
        success=False,
        message=reason,
        findings=record.findings,
        metadata={"skipped": True},
    )


def _dry_run_evidence(record: DocumentRecord, chunks: Sequence[Any], findings: Sequence[SecurityFinding]) -> str:
    risk = format_findings(findings) if findings else "none"
    return f"### {record.relative_path}\nDRY RUN: would process {len(chunks)} chunk(s). Security findings: {risk}."


def _fallback_evidence_note(chunk: TextChunk, exc: Exception) -> str:
    excerpt = chunk.text.strip().replace("\n", " ")
    if len(excerpt) > 1200:
        excerpt = excerpt[:1200] + "..."
    return (
        "LLM evidence extraction failed for this chunk, so LAMB used a local evidence excerpt instead.\n"
        f"Failure: {exc}\n"
        f"Fallback excerpt: {excerpt}"
    )


def _processed_message(chunks: int, llm_fallbacks: int = 0) -> str:
    message = f"processed {chunks} chunk(s)"
    if llm_fallbacks:
        message += f" with {llm_fallbacks} local evidence fallback(s)"
    return message


def _dry_run_research_report(question: str, sources: Sequence[str], evidence: Sequence[str], skipped: Sequence[str]) -> str:
    source_lines = "\n".join(f"- {source}" for source in sources) or "- 无"
    skipped_lines = "\n".join(f"- {source}" for source in skipped) or "- 无"
    evidence_preview = "\n\n".join(evidence) or "无"
    return f"""# LAMB Dry-Run Research Report

## Question
{question}

## Sources That Would Be Processed
{source_lines}

## Skipped Files
{skipped_lines}

## Planned Evidence Notes
{evidence_preview}
"""


def _fallback_research_report(
    question: str,
    sources: Sequence[str],
    evidence: Sequence[str],
    skipped: Sequence[str],
    exc: Exception,
) -> str:
    source_lines = "\n".join(f"- {source}" for source in sources) or "- none"
    skipped_lines = "\n".join(f"- {source}" for source in skipped) or "- none"
    evidence_preview = "\n\n".join(evidence) or "none"
    return f"""# LAMB Fallback Research Report

## Question
{question}

## Why This Fallback Was Used
The LLM reduce stage failed after retries, so LAMB preserved the collected evidence notes instead of dropping the run.

Failure: {exc}

## Sources
{source_lines}

## Skipped Files
{skipped_lines}

## Evidence Notes
{evidence_preview}
"""


def _text_output_extension(output_format: str) -> str:
    normalized = output_format.lower().lstrip(".")
    if normalized == "markdown":
        return "md"
    if normalized in {"md", "txt", "docx"}:
        return normalized
    raise ValueError("output_format must be one of: md, markdown, txt, docx")


def _extract_json_object(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError(f"LLM output did not contain a JSON object: {text[:120]}")
        value = json.loads(cleaned[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("LLM extraction output must be a JSON object")
    return value


def _merge_extraction_rows(fields: Sequence[str], rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    merged = {field: "" for field in fields}
    for row in rows:
        for field in fields:
            value = row.get(field)
            if value not in (None, "", []):
                if not merged[field]:
                    merged[field] = value
                elif merged[field] != value:
                    merged[field] = f"{merged[field]}; {value}"
    return merged


def _normalize_fields(fields: Sequence[str]) -> List[str]:
    normalized = []
    seen = set()
    for field in fields:
        field_name = str(field).strip()
        if not field_name or field_name in seen:
            continue
        normalized.append(field_name)
        seen.add(field_name)
    if not normalized:
        raise ValueError("fields must contain at least one non-empty field")
    return normalized


def _normalize_extraction_format(output_format: str) -> str:
    normalized = output_format.lower().lstrip(".")
    if normalized not in {"csv", "json"}:
        raise ValueError("output_format must be csv or json")
    return normalized


def _fields_from_instruction(instruction: str) -> List[str]:
    separators = [",", "，", ";", "；", "\n"]
    text = instruction
    for separator in separators[1:]:
        text = text.replace(separator, separators[0])
    fields = [part.strip() for part in text.split(",") if part.strip()]
    if len(fields) >= 2 and all(len(field) <= 24 for field in fields):
        return fields
    return ["摘要", "关键结论", "备注"]
