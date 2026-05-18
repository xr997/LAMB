# LAMB

**Local-first, safety-aware AI assistant for processing entire folders of documents.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-lamb-orange)](#quick-demo)
[![Safety](https://img.shields.io/badge/Safety-Prompt%20Injection%20Aware-red)](docs/security-model.md)

Chinese version: [README.zh.md](README.zh.md)

> Give LAMB a folder. It scans, parses, safety-checks, chunks, calls an LLM, exports results, and writes an audit manifest.

---

## Why LAMB

Web AI tools are convenient for a single file, but they become fragile when the input is an entire folder.

| Pain | What usually happens | How LAMB helps |
| --- | --- | --- |
| Too many files | Files are uploaded one by one | Scan and process a local folder |
| Long documents | Context overflow and unstable answers | Chunking plus map-reduce style workflows |
| Messy outputs | Manual copy-paste into tables and reports | Export Markdown, CSV, JSON, and DOCX |
| No traceability | No reliable record of inputs or failures | Write a `manifest.json` audit trail for each run |
| Prompt injection | Documents may contain instructions such as "ignore previous instructions" | Treat documents as untrusted evidence and record risk findings |

LAMB is not another chat interface. It turns a local document folder into a reproducible, auditable, reusable LLM document workflow.

---

## What LAMB Does

```text
folder
  -> scan files
  -> parse text
  -> safety check
  -> chunk long documents
  -> LLM batch processing / multi-document QA / field extraction
  -> export results
  -> write audit manifest
```

### Core Capabilities

- **Multi-document research QA**: ask questions across papers, reports, meeting notes, or course materials, then generate a cited Markdown report.
- **Batch document processing**: summarize, translate, polish, review, or grade every file in a folder.
- **Structured field extraction**: extract fields from homework, resumes, meeting notes, and reports into CSV or JSON.
- **Safety-aware processing**: detect prompt injection, redact sensitive values, and skip high-risk documents in strict mode.
- **Long-document handling**: split long inputs into chunks to reduce context-overflow risk.
- **Installable, importable, executable**: use it as a Python library or as the `lamb` command-line tool.

---

## Daily Use Cases

| Scenario | Example command | Output |
| --- | --- | --- |
| Grade assignments | `lamb extract homework --fields "Name,Score,Comment,Main Issues"` | CSV grading table |
| Read papers | `lamb research papers --question "How do these papers differ in methods?"` | Cited research report |
| Organize meeting notes | `lamb extract meetings --fields "Topic,Action Item,Owner,Deadline"` | Action-item table |
| Screen resumes | `lamb extract resumes --fields "Name,Education,Skills,Projects"` | Candidate table |
| Synthesize reports | `lamb research reports --question "What trends do these reports share?"` | Cross-document summary |
| Safe preview | `lamb research docs --question "What do these documents discuss?" --dry-run` | Plan without LLM calls |

---

## Quick Demo

Install:

```bash
git clone https://github.com/xr997/LAMB.git
cd LAMB
pip install -e .
```

Configure an OpenAI-compatible LLM:

```bash
cp .env.example .env
```

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
```

Scan a folder:

```bash
lamb scan data/inputs
```

Ask a question across documents:

```bash
lamb research data/inputs --question "What are the shared conclusions across these documents?"
```

Extract a grading table:

```bash
lamb extract data/inputs --fields "Name,Score,Comment,Main Issues" --redact
```

Summarize every file:

```bash
lamb batch data/inputs --instruction "Write a concise 200-word summary for this document." --format md
```

Preview a workflow without calling an LLM:

```bash
lamb research data/inputs --question "What do these documents discuss?" --dry-run
```

---

## Python SDK

```python
from lamb import answer_over_directory, extract_fields, process_directory, scan_documents

records = scan_documents("data/inputs")

qa = answer_over_directory(
    input_dir="data/inputs",
    question="What are the shared conclusions across these documents?",
    output_dir="data/outputs",
    redact=True,
)

extraction = extract_fields(
    input_dir="data/inputs",
    fields=["Name", "Score", "Comment"],
    output_dir="data/outputs",
)

batch = process_directory(
    input_dir="data/inputs",
    instruction="Generate a clear summary for each document.",
    output_format="md",
)
```

---

## Safety Model

LAMB does not focus on transport-layer security. Its focus is **LLM application-layer safety** for real document workflows.

- Document content is wrapped as `<UNTRUSTED_DOCUMENT>` and treated as evidence, not instructions.
- Prompt builders explicitly forbid following commands embedded in document text.
- Prompt-injection signals are detected and recorded.
- `--strict-security` skips high-risk documents.
- `--redact` masks emails, phone numbers, API keys, tokens, and JWT-like strings.
- Hidden files are skipped by default and can be included explicitly with `--include-hidden`; `.env`, credential-like files, and symbolic links are still refused.
- Every run writes an audit manifest with inputs, outputs, parameters, risk findings, failures, and elapsed time.

Read more: [Security Model](docs/security-model.md)

---

## Outputs

Depending on the workflow, LAMB writes:

- Markdown research reports
- CSV or JSON extraction tables
- Per-document Markdown, TXT, or DOCX outputs
- `*_manifest.json` audit files

---

## System Overview

![LAMB system overview](docs/assets/lamb-system-overview.png)

---

## Documentation

- [Quickstart](docs/quickstart.md)
- [Python API](docs/api.md)
- [Examples](docs/examples.md)
- [Security Model](docs/security-model.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## Development

```bash
python -m compileall lamb tests
python -m unittest discover -s tests
```

Run real LLM integration tests manually:

```bash
RUN_REAL_LLM_TESTS=1 python -m unittest tests.test_real_llm_integration
```

---

## License

MIT License.
