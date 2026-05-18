# LAMB

**Local-first AI Multi-document Batch Assistant**<br>
**本地优先的安全可信多文档批处理与研究助理**

[English](#english) | [中文](#中文)

---

## English

LAMB is a local-first assistant for processing folders of documents with LLMs. It helps users read papers, grade assignments, summarize reports, extract structured fields, organize meeting notes, and answer questions across many files.

The project is designed as both a **Python library** and an **executable CLI tool**. It can be imported by third-party programs, installed with `pip`, and used directly through the `lamb` command.

LAMB also treats document content as untrusted input. It includes prompt-injection detection, optional sensitive-data redaction, long-document chunking, path safety checks, and per-run audit manifests.

### Why LAMB

Web-based AI tools are convenient for one document, but they become painful when you need to process an entire folder:

- Uploading files one by one is slow.
- Long documents can exceed context limits.
- Results are hard to save as CSV, Markdown, DOCX, or JSON.
- It is difficult to track which files succeeded or failed.
- Documents may contain prompt-injection text such as "ignore previous instructions".

LAMB turns a local document folder into a reproducible LLM workflow: scan, parse, secure, chunk, process, export, and audit.

### Core Features

- **Multi-document research QA**: ask questions across a folder and generate a Markdown report with source references.
- **Batch document processing**: summarize, translate, polish, review, or grade each document.
- **Structured extraction**: extract fields from resumes, homework, meeting notes, reports, and papers into CSV or JSON.
- **Safe LLM processing**: detect prompt injection, skip risky files in strict mode, and optionally redact sensitive values.
- **Long-document support**: split documents into chunks and use map-reduce style workflows.
- **Audit manifests**: write a `manifest.json` for every run with inputs, outputs, model, parameters, findings, failures, and elapsed time.
- **SDK + CLI**: usable from Python code and from the command line.

### Installation

Install from a local clone:

```bash
git clone https://github.com/xr997/LAMB.git
cd LAMB
pip install -e .
```

Install directly from GitHub:

```bash
pip install git+https://github.com/xr997/LAMB.git
```

Create a `.env` file:

```bash
cp .env.example .env
```

Example configuration:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
```

LAMB uses an OpenAI-compatible chat API. You can use DeepSeek, OpenAI-compatible gateways, or local compatible servers by changing `LLM_BASE_URL`.

### CLI Quickstart

Scan a folder:

```bash
lamb scan data/inputs
```

Ask a question across papers or reports:

```bash
lamb research data/inputs --question "What are the common conclusions across these documents?"
```

Grade assignments into a CSV table:

```bash
lamb extract data/inputs --fields "Name,Score,Comment,Main Issues" --redact
```

Summarize each document:

```bash
lamb batch data/inputs --instruction "Write a concise 200-word summary for this document." --format md
```

Preview a workflow without calling an LLM:

```bash
lamb research data/inputs --question "What do these documents discuss?" --dry-run
```

### Python SDK

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

### Safety Model

LAMB treats document text as evidence, not as instructions. Its safety-oriented processing includes:

- Wrapping document content inside `<UNTRUSTED_DOCUMENT>` boundaries.
- Prompt instructions that forbid following commands embedded in documents.
- Detection of common prompt-injection attempts.
- Default skipping for hidden files, `.env`, credential-like files, and symbolic links.
- Optional redaction for emails, phone numbers, API keys, tokens, and JWT-like strings.
- Strict mode for skipping high-risk documents.

See [docs/security-model.md](docs/security-model.md) for details.

### Development

```bash
python -m compileall lamb tests
python -m unittest discover -s tests
```

Project documentation:

- [Quickstart](docs/quickstart.md)
- [Python API](docs/api.md)
- [Examples](docs/examples.md)
- [Security Model](docs/security-model.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

### License

MIT License.

---

## 中文

LAMB 是一个本地优先的安全可信多文档处理助理。它面向日常资料夹中的 Word、PDF、Markdown、TXT、CSV、JSON 文档，帮助用户批量读论文、改作业、总结报告、抽取结构化字段、整理会议纪要，并围绕多个文件回答问题。

项目同时提供 **Python 库** 和 **命令行工具** 两种形态。第三方程序可以 `import lamb` 引用它，用户也可以通过 `pip install` 安装后直接运行 `lamb` 命令。

LAMB 不把文档内容当作可信指令，而是当作待分析证据处理。它内置 Prompt 注入检测、可选敏感信息脱敏、长文档分块、路径安全检查和每次运行的审计清单。

### 为什么需要 LAMB

网页端 AI 工具适合处理单个文件，但一旦面对整个文件夹，就会出现明显痛点：

- 一个个上传文件效率低。
- 长文档容易超过上下文限制。
- 结果难以稳定导出为 CSV、Markdown、DOCX 或 JSON。
- 很难追踪哪些文件成功、哪些失败。
- 文档中可能包含 “忽略之前的指令” 等 Prompt 注入内容。

LAMB 把本地资料夹变成一条可复现的 LLM 工作流：扫描、解析、安全检查、分块、处理、导出和审计。

### 核心功能

- **多文档研究问答**：跨整个资料夹回答问题，生成带来源引用的 Markdown 报告。
- **批量文档处理**：对每份文档执行摘要、翻译、润色、审阅、批改等任务。
- **结构化抽取**：从简历、作业、会议纪要、报告、论文中抽取字段，输出 CSV 或 JSON。
- **安全可信处理**：检测 Prompt 注入，严格模式下跳过高风险文件，可选敏感信息脱敏。
- **长文档支持**：自动分块，并使用 map-reduce 风格工作流降低上下文超限风险。
- **审计记录**：每次运行生成 `manifest.json`，记录输入、输出、模型、参数、风险提示、失败原因和耗时。
- **SDK + CLI**：既可以被 Python 程序引用，也可以作为命令行软件运行。

### 安装

从本地仓库安装：

```bash
git clone https://github.com/xr997/LAMB.git
cd LAMB
pip install -e .
```

也可以从 GitHub 直接安装：

```bash
pip install git+https://github.com/xr997/LAMB.git
```

创建 `.env` 文件：

```bash
cp .env.example .env
```

配置示例：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
```

LAMB 使用 OpenAI-compatible Chat API。可以通过修改 `LLM_BASE_URL` 接入 DeepSeek、OpenAI 兼容网关或本地兼容服务。

### CLI 快速上手

扫描资料夹：

```bash
lamb scan data/inputs
```

跨论文或报告提问：

```bash
lamb research data/inputs --question "这些文档的共同结论是什么？"
```

批量批改作业并输出 CSV：

```bash
lamb extract data/inputs --fields "姓名,分数,评语,主要问题" --redact
```

为每份文档生成摘要：

```bash
lamb batch data/inputs --instruction "请为这份文档写一段 200 字摘要" --format md
```

不调用 LLM，只预览工作流：

```bash
lamb research data/inputs --question "这些文档主要讨论了什么？" --dry-run
```

### Python SDK

```python
from lamb import answer_over_directory, extract_fields, process_directory, scan_documents

records = scan_documents("data/inputs")

qa = answer_over_directory(
    input_dir="data/inputs",
    question="这些文档的共同结论是什么？",
    output_dir="data/outputs",
    redact=True,
)

extraction = extract_fields(
    input_dir="data/inputs",
    fields=["姓名", "分数", "评语"],
    output_dir="data/outputs",
)

batch = process_directory(
    input_dir="data/inputs",
    instruction="请为每份文档生成结构清晰的摘要",
    output_format="md",
)
```

### 安全模型

LAMB 将文档文本视为证据，而不是指令来源。默认安全策略包括：

- 将文档内容包裹在 `<UNTRUSTED_DOCUMENT>` 边界中。
- 在 Prompt 中明确禁止执行文档内部指令。
- 检测常见 Prompt 注入尝试。
- 默认跳过隐藏文件、`.env`、凭据类文件和符号链接。
- 可选脱敏邮箱、手机号、API key、token、JWT 类字符串。
- 严格模式下跳过高风险文档。

更多细节见 [docs/security-model.md](docs/security-model.md)。

### 开发

```bash
python -m compileall lamb tests
python -m unittest discover -s tests
```

项目文档：

- [快速上手](docs/quickstart.md)
- [Python API](docs/api.md)
- [示例场景](docs/examples.md)
- [安全模型](docs/security-model.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

### 许可证

MIT License.
