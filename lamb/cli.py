"""Command line interface for LAMB."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Sequence

from . import __version__
from .scanning import scan_documents, summarize_scan
from .workflow import answer_over_directory, extract_fields, process_directory


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "version":
            print(f"LAMB {__version__}")
            return 0
        if args.command == "scan":
            return _cmd_scan(args)
        if args.command == "research":
            return _cmd_research(args)
        if args.command == "extract":
            return _cmd_extract(args)
        if args.command == "batch":
            return _cmd_batch(args)
        parser.print_help()
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lamb",
        description="Local-first safe LLM assistant for multi-document research and batch processing.",
    )
    parser.add_argument("--version", action="version", version=f"LAMB {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    scan = subparsers.add_parser("scan", help="Scan a folder and show supported/skipped documents.")
    scan.add_argument("input_dir")
    scan.add_argument("--include-hidden", action="store_true", help="Include hidden files. Sensitive names are still skipped.")
    scan.add_argument("--max-file-size-mb", type=int, default=50)
    scan.add_argument("--hash", action="store_true", help="Compute SHA-256 for supported files.")
    scan.set_defaults(command="scan")

    research = subparsers.add_parser("research", help="Answer a question over a folder of documents.")
    research.add_argument("input_dir")
    research.add_argument("--question", required=True)
    _add_common_run_args(research)
    research.set_defaults(command="research")

    extract = subparsers.add_parser("extract", help="Extract structured fields from each document.")
    extract.add_argument("input_dir")
    extract.add_argument("--fields", required=True, help="Comma-separated fields, e.g. 姓名,分数,评语")
    extract.add_argument("--format", choices=["csv", "json"], default="csv", dest="output_format")
    _add_common_run_args(extract)
    extract.set_defaults(command="extract")

    batch = subparsers.add_parser("batch", help="Run a free-form instruction against every document.")
    batch.add_argument("input_dir")
    batch.add_argument("--instruction", required=True)
    batch.add_argument("--format", choices=["md", "txt", "docx"], default="docx", dest="output_format")
    _add_common_run_args(batch)
    batch.set_defaults(command="batch")

    version = subparsers.add_parser("version", help="Print LAMB version.")
    version.set_defaults(command="version")
    return parser


def _add_common_run_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-dir", default="data/outputs")
    parser.add_argument("--dry-run", action="store_true", help="Preview the workflow without calling an LLM.")
    parser.add_argument("--strict-security", action="store_true", help="Skip documents with high-risk prompt injection signals.")
    parser.add_argument("--redact", action="store_true", help="Redact common sensitive values before LLM processing.")
    parser.add_argument("--model", help="OpenAI-compatible model name. Overrides LLM_MODEL.")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum characters per LLM chunk.")


def _cmd_scan(args: argparse.Namespace) -> int:
    records = scan_documents(
        args.input_dir,
        include_hidden=args.include_hidden,
        max_file_size_mb=args.max_file_size_mb,
        compute_hash=args.hash,
    )
    summary = summarize_scan(records)
    print("LAMB scan")
    print(f"  total:      {summary['total']}")
    print(f"  supported:  {summary['supported']}")
    print(f"  skipped:    {summary['skipped']}")
    print(f"  unsupported:{summary['unsupported']}")
    for record in records:
        status = "OK" if record.supported and not record.skipped else "SKIP"
        reason = f" - {record.skip_reason}" if record.skip_reason else ""
        print(f"  [{status}] {record.relative_path} ({record.extension or 'no-ext'}, {record.size_bytes} bytes){reason}")
    return 0


def _cmd_research(args: argparse.Namespace) -> int:
    result = answer_over_directory(
        input_dir=args.input_dir,
        question=args.question,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        strict_security=args.strict_security,
        redact=args.redact,
        model_name=args.model,
        max_chars=args.max_chars,
    )
    print(result.answer)
    print(f"\nreport: {result.report_path}")
    print(f"manifest: {result.manifest_path}")
    return 0 if result.ok else 1


def _cmd_extract(args: argparse.Namespace) -> int:
    fields = _parse_fields(args.fields)
    result = extract_fields(
        input_dir=args.input_dir,
        fields=fields,
        output_dir=args.output_dir,
        output_format=args.output_format,
        dry_run=args.dry_run,
        strict_security=args.strict_security,
        redact=args.redact,
        model_name=args.model,
        max_chars=args.max_chars,
    )
    print(f"rows: {len(result.rows)}")
    print(f"output: {result.output_path}")
    print(f"manifest: {result.manifest_path}")
    return 0 if result.ok else 1


def _cmd_batch(args: argparse.Namespace) -> int:
    result = process_directory(
        input_dir=args.input_dir,
        instruction=args.instruction,
        mode="mapping",
        output_dir=args.output_dir,
        output_format=args.output_format,
        dry_run=args.dry_run,
        strict_security=args.strict_security,
        redact=args.redact,
        model_name=args.model,
        max_chars=args.max_chars,
    )
    print(f"run_id: {result.run_id}")
    print(f"total: {result.total}, succeeded: {result.succeeded}, failed: {result.failed}, skipped: {result.skipped}")
    for file_result in result.files:
        status = "OK" if file_result.success else "SKIP" if file_result.metadata.get("skipped") else "FAIL"
        suffix = f" -> {file_result.output_path}" if file_result.output_path else ""
        print(f"  [{status}] {file_result.input_path}: {file_result.message}{suffix}")
    print(f"manifest: {result.manifest_path}")
    return 0 if result.ok else 1


def _parse_fields(raw: str) -> list[str]:
    normalized = raw.replace("，", ",").replace("；", ",").replace(";", ",")
    fields = [field.strip() for field in normalized.split(",") if field.strip()]
    if not fields:
        raise ValueError("--fields must contain at least one field")
    return fields


if __name__ == "__main__":
    raise SystemExit(main())
