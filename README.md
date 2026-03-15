# 🚀 OmniBatch-LLM: 自动化大模型批量处理框架

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

OmniBatch-LLM 是一个专为开发者和研究人员设计的轻量级、高扩展大模型批量任务处理框架。

在面对海量本地文档时，传统的单次 API 调用脚本往往面临代码冗余、难以扩展和缺乏有效管理等痛点。本项目致力于打通“本地文件系统”与“大语言模型 API”之间的工程壁垒，提供一套高内聚、低耦合的自动化工作流。它非常适合用于构建人机协同（Human-AI Collaboration）的自动化文档分析管线。

## 💡 核心应用场景

* **学术文献处理**：批量提取、清洗并分类数千篇学术会议论文的内容与核心摘要。
* **自动化教育评估**：针对学生提交的海量 Word/TXT 作业，结合标准答案 Prompt 进行批量批改与结构化打分。
* **语料库构建**：为 RAG（检索增强生成）系统或大模型微调自动化生成高质量的 QA 数据集。

## 🧩 核心特性

* **👁️ 多格式解析 (Parsers)**：内置 `txt` 和 `docx` 智能解析器，支持一键读取包含表格的复杂 Word 文档。
* **🧠 动态提示词引擎 (Templates)**：将提取的长文本无缝注入外部 Prompt 模板，指令与代码完全解耦。
* **⚡ 高可用模型中枢 (Core)**：全面兼容 OpenAI SDK 格式，完美支持 DeepSeek 等高性价比 API，并可无缝切换至本地 vLLM 部署接口。内置异常拦截机制，单文件报错不阻断全局任务。
* **✍️ 自动化结果生成 (Writers)**：支持将大模型的结构化输出原样重组并持久化为新的 `.docx` 或 `.txt` 报告。

## 🚀 快速上手 (Quickstart)

### 1. 环境准备
确保你的环境中已安装 Python 3.8+。克隆项目后，安装核心依赖：
```bash
git clone [https://github.com/你的用户名/omnibatch-llm.git](https://github.com/你的用户名/omnibatch-llm.git)
cd omnibatch-llm
pip install -r requirements.txt

```

### 2. 配置密钥

在项目根目录创建 `.env` 文件，并填入你的模型 API Key（默认配置为 DeepSeek，你也可以修改 `LLM_BASE_URL` 切换到其他模型）：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=[https://api.deepseek.com](https://api.deepseek.com)

```

### 3. 运行你的首个批量任务

1. 将需要处理的文件（`.txt` 或 `.docx`）放入 `data/inputs/` 目录。
2. （可选）修改 `data/prompt.txt` 中的自定义指令。
3. 执行主程序：

```bash
python main.py

```

处理完成后，结果将自动生成并保存在 `data/outputs/` 目录中。

---

## 📝 更新日志 (Changelog)

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/) 规范。

### [v0.1.0] - 2026-03-15 (MVP 初始发布)

**🎉 Added (新增)**

* 构建项目核心架构：分为 `core`, `parsers`, `templates`, `writers`, `utils` 五个高度解耦的模块。
* `parsers`: 新增 `BaseParser` 接口，支持 `.txt` 和 `.docx`（含表格文本）的基础读取与提取。
* `templates`: 新增基于外部 `.txt` 文件的 Prompt 动态加载与变量填充引擎。
* `core`: 封装兼容 OpenAI 格式的大模型网络请求引擎，默认集成 DeepSeek API，内置基础异常捕获。
* `writers`: 新增 `BaseWriter` 接口，支持将模型输出结构化保存为独立的 `.txt` 和 `.docx` 文件。
* `main.py`: 实现 MVP 阶段的端到端工作流自动化执行脚本。

### [Unreleased] (开发中/待发布)

* **[CLI]** 将 `main.py` 升级为基于 `argparse` 或 `Click` 的标准命令行工具。
* **[Core]** 引入高并发异步调度器（Asyncio），极大提升批量处理速度并增加 API 速率限制控制。
* **[Parsers]** 增加对 PDF 和 Markdown 文件的结构化解析支持。
* **[UI]** 增加基于 Gradio 的轻量级 Web 交互界面。

---

## 🤝 参与贡献 (Contributing)

欢迎任何形式的贡献！无论是提交 Issue 报告 Bug、增加新的文件解析器（如新增 `pdf_parser.py`）、还是优化 Prompt 模板，我们都非常期待您的 Pull Request。详细规范请参阅（即将发布的） `CONTRIBUTING.md`。

## 📄 开源协议 (License)

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 协议开源。

