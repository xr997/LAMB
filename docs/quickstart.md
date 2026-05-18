# Quickstart

This guide shows the shortest path from clone to a working LAMB command.

## Install

```bash
git clone https://github.com/xr997/LAMB.git
cd LAMB
pip install -e .
```

## Configure

Create `.env` in the project root:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
```

LAMB uses an OpenAI-compatible chat API. DeepSeek, OpenAI-compatible gateways, and local compatible servers can be used by changing `LLM_BASE_URL`.

## Dry Run First

Dry-run mode does not call an LLM. It is useful for checking scanned files and output paths.

```bash
lamb scan data/inputs
lamb research data/inputs --question "这些文档的共同结论是什么？" --dry-run
```

## Common Workflows

Batch summarize documents:

```bash
lamb batch data/inputs --instruction "请为这份文档写一段摘要" --format md
```

Extract homework grading fields:

```bash
lamb extract data/inputs --fields "姓名,分数,评语" --redact
```

Ask a question across papers:

```bash
lamb research data/inputs --question "这些论文的方法有什么共同点和差异？"
```

## Outputs

All commands write artifacts under `data/outputs` by default:

- Markdown, DOCX, TXT, CSV, or JSON result files.
- A `*_manifest.json` audit file for each run.

The manifest records input files, model name, parameters, security findings, failures, and elapsed time.

LAMB also writes `latest_index.md` in the output directory. It lists the latest run id, generated output files, manifest path, and success/failure counts.
