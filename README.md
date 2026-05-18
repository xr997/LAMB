# LAMB

**Local-first, safety-aware AI assistant for processing an entire folder of documents.**
**本地优先、安全可信的多文档 AI 批处理与研究助理。**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-lamb-orange)](#quick-demo--快速演示)
[![Safety](https://img.shields.io/badge/Safety-Prompt%20Injection%20Aware-red)](docs/security-model.md)

> Drop in a folder. Ask a question. Get cited answers, CSV tables, per-file outputs, and an audit trail.
> 放入一个资料夹，提出一个问题，获得带来源的答案、CSV 表格、逐文件结果和可审计运行记录。

---

## The Problem / 痛点

Most AI tools are great for **one file** and painful for **one folder**.

大多数 AI 工具处理单个文件很方便，但面对整个资料夹就会变得低效且不可控。

| Pain / 问题 | What usually happens / 常见结果 | How LAMB helps / LAMB 的解决方式 |
| --- | --- | --- |
| Too many files / 文件太多 | Upload files one by one / 一个个上传 | Scan and process a folder locally / 本地扫描并批量处理资料夹 |
| Long documents / 文档太长 | Context overflow, unstable answers / 超上下文、回答不稳定 | Chunking + map-reduce / 自动分块与汇总 |
| Messy outputs / 输出难整理 | Copy-paste into spreadsheets / 手工复制到表格 | Export CSV, JSON, Markdown, DOCX / 直接导出结构化结果 |
| Trust issues / 结果不可追溯 | No record of inputs or failures / 不知道处理了哪些文件 | Per-run `manifest.json` audit trail / 每次运行生成审计清单 |
| Prompt injection / 文档内恶意指令 | Documents may say "ignore previous instructions" / 文档可能诱导模型越权 | Treat documents as untrusted evidence / 将文档视为不可信证据 |

---

## What LAMB Does / LAMB 能做什么

LAMB turns a local document folder into a safe, repeatable LLM workflow:

LAMB 将本地资料夹变成一条安全、可复现的 LLM 工作流：

```text
documents -> scan -> parse -> safety check -> chunk -> LLM workflow -> export -> manifest
文档资料夹 -> 扫描 -> 解析 -> 安全检查 -> 分块 -> LLM 工作流 -> 导出 -> 审计清单
```

### Core Capabilities / 核心能力

- **Research across documents / 多文档研究问答**
  Ask questions across papers, reports, meeting notes, or class materials, then get a cited Markdown report.
  跨论文、报告、会议纪要、课程材料提问，输出带来源引用的 Markdown 报告。

- **Batch processing / 批量处理**
  Summarize, translate, polish, review, or grade every document in a folder.
  对资料夹内每份文档执行摘要、翻译、润色、审阅、批改等任务。

- **Structured extraction / 结构化抽取**
  Extract fields into CSV/JSON, such as assignment scores, resume skills, meeting action items, or report conclusions.
  将作业分数、简历技能、会议待办、报告结论等字段抽取成 CSV/JSON。

- **Safety-aware LLM processing / 安全可信处理**
  Detect prompt injection, optionally redact sensitive values, skip risky documents in strict mode, and record all findings.
  检测 Prompt 注入，可选敏感信息脱敏，严格模式下跳过高风险文档，并记录风险发现。

- **SDK + CLI / 库与命令行双入口**
  Use it as `import lamb` in Python, or install it as an executable `lamb` command.
  既可作为 Python 库被第三方程序引用，也可作为 `lamb` 命令行软件运行。

---

## Daily Use Cases / 日常应用场景

| Scenario / 场景 | Example command / 示例命令 | Output / 输出 |
| --- | --- | --- |
| Grade assignments / 批量批改作业 | `lamb extract homework --fields "姓名,分数,评语,主要问题"` | CSV grading table / 批改表 |
| Read papers / 批量读论文 | `lamb research papers --question "这些论文的方法有什么异同？"` | Cited research report / 带来源综述 |
| Meeting notes / 整理会议纪要 | `lamb extract meetings --fields "议题,待办,负责人,截止时间"` | Action-item table / 待办表 |
| Resume screening / 筛选简历 | `lamb extract resumes --fields "姓名,教育背景,技能,项目经验"` | Candidate table / 候选人表 |
| Report synthesis / 汇总调研报告 | `lamb research reports --question "这些报告共同反映了什么趋势？"` | Cross-document summary / 跨文档总结 |
| Safe preview / 安全预览 | `lamb research docs --question "这些文档说了什么？" --dry-run` | Plan without API calls / 不调用模型的预览 |

---

## Quick Demo / 快速演示

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
lamb research data/inputs --question "这些文档的共同结论是什么？"
```

Extract a grading table:

```bash
lamb extract data/inputs --fields "姓名,分数,评语,主要问题" --redact
```

Summarize each file:

```bash
lamb batch data/inputs --instruction "请为这份文档写一段 200 字摘要" --format md
```

Preview without calling an LLM:

```bash
lamb research data/inputs --question "这些文档主要讨论了什么？" --dry-run
```

---

## Python SDK / Python 调用

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

---

## Safety Model / 安全模型

LAMB's safety goal is not network encryption. Its focus is **LLM application-layer safety** for real document workflows.

LAMB 的安全重点不是传统通信加密，而是面向真实文档工作流的 **LLM 应用层安全**。

- Documents are wrapped as `<UNTRUSTED_DOCUMENT>` evidence, not treated as instructions.
  文档被包裹为 `<UNTRUSTED_DOCUMENT>` 证据，而不是指令来源。
- Prompt builders explicitly forbid following commands embedded in document text.
  Prompt 明确禁止执行文档内部的反向指令。
- Prompt-injection signals are detected and recorded.
  检测并记录 Prompt 注入风险。
- `--strict-security` skips high-risk documents.
  `--strict-security` 会跳过高风险文档。
- `--redact` masks emails, phone numbers, API keys, tokens, and JWT-like strings.
  `--redact` 会脱敏邮箱、手机号、API key、token、JWT 类字符串。
- Hidden files, `.env`, credential-like files, and symbolic links are skipped by default.
  默认跳过隐藏文件、`.env`、凭据类文件和符号链接。
- Every run writes a manifest with inputs, outputs, parameters, risk findings, failures, and elapsed time.
  每次运行都会记录输入、输出、参数、风险提示、失败原因和耗时。

Read more: [Security Model](docs/security-model.md)

---

## Outputs / 输出物

Depending on the workflow, LAMB writes:

LAMB 会根据工作流输出：

- Markdown research reports / Markdown 研究报告
- CSV or JSON extraction tables / CSV 或 JSON 抽取表
- Per-document Markdown, TXT, or DOCX files / 每份文档对应的 Markdown、TXT 或 DOCX 结果
- `*_manifest.json` audit files / `*_manifest.json` 审计清单

---

## Project Image Prompt / 项目介绍图绘图 Prompt

Use this prompt to generate a README hero image or competition poster. Recommended aspect ratio: **16:9**.

可以使用下面的 prompt 生成 README 首图或比赛展示图。推荐比例：**16:9**。

```text
A polished 16:9 hero illustration for an open-source AI software project named LAMB. Show a local computer workspace where a folder full of documents, PDFs, Word files, papers, homework, resumes, and meeting notes flows into a secure AI processing pipeline. The pipeline has clear stages: scan, parse, safety check, chunk, analyze, export, audit. Include visual metaphors of a shield protecting the document stream from prompt injection, long documents being split into small chunks, and final outputs becoming a cited research report, a CSV table, and per-file summaries. Style: modern technical product illustration, clean UI panels, subtle depth, high contrast, trustworthy and energetic, blue/teal/white with small orange accents, open-source developer aesthetic, no clutter, no readable small text except a clean optional title area for "LAMB". Avoid cartoon animals, avoid cyberpunk darkness, avoid random fake text, avoid logos of real companies.
```

中文绘图提示词：

```text
为一个名为 LAMB 的开源 AI 软件项目绘制 16:9 首图。画面展示本地电脑工作台，一个装满 PDF、Word、论文、作业、简历、会议纪要的资料夹进入安全的 AI 文档处理流水线。流水线阶段包括：扫描、解析、安全检查、分块、分析、导出、审计。用盾牌表现 Prompt 注入防护，用长文档被切成多个片段表现长文档分块，用最终生成的带来源研究报告、CSV 表格、逐文件摘要表现输出结果。风格为现代技术产品插画，干净的 UI 面板，轻微空间层次，高对比度，可信而有活力，蓝色、青绿色、白色为主，少量橙色点缀，开源开发者气质，不杂乱。不要卡通动物，不要黑暗赛博朋克，不要随机乱码文字，不要真实公司 logo，预留一个干净区域用于后期叠加标题 “LAMB”。
```

---

## Documentation / 文档

- [Quickstart / 快速上手](docs/quickstart.md)
- [Python API](docs/api.md)
- [Examples / 示例场景](docs/examples.md)
- [Security Model / 安全模型](docs/security-model.md)
- [Contributing / 贡献指南](CONTRIBUTING.md)
- [Changelog / 更新日志](CHANGELOG.md)

---

## Development / 开发

```bash
python -m compileall lamb tests
python -m unittest discover -s tests
```

Run real LLM integration tests manually:

```bash
RUN_REAL_LLM_TESTS=1 python -m unittest tests.test_real_llm_integration
```

---

## License / 许可证

MIT License.
