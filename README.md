# 🚀 OmniBatch-LLM: 基于 MCP 协议的自动化文档处理智能体

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: MCP](https://img.shields.io/badge/Architecture-MCP_Agent-purple.svg)](https://modelcontextprotocol.io/)

OmniBatch-LLM 是一个专为开发者和研究人员设计的高级文档批处理框架。**本项目原生采用了前沿的 Model Context Protocol (MCP) 架构**，将传统的静态批处理脚本升级为可通过自然语言驱动的 AI 智能体 (Agent)。

面对海量本地文档（如学术论文解析、自动化作业评估），您无需再编写繁琐的调度代码。只需在内置的极客终端中输入一句自然语言指令，系统的大脑（如 DeepSeek）便会自动拆解意图、寻址本地文件夹、调用底层的解析与生成工具，实现“感知-思考-执行-反馈”的全自动工作流。

## 💡 核心应用场景

* **学术文献处理**：批量提取、清洗并分类数千篇学术会议论文的内容与核心摘要。
* **自动化教育评估**：针对学生提交的海量 Word/TXT 作业，结合标准答案 Prompt 进行批量批改与结构化打分。
* **语料库构建**：为 RAG（检索增强生成）系统或大模型微调自动化生成高质量的 QA 数据集。

## 🧩 核心架构亮点 (MCP Agent)

本项目采用标准的 Client-Server 智能体分离架构：

* **🧠 智能体大脑 (Client)**：内置基于 `rich` 构建的绚丽终端交互界面。使用 `asyncio` 实现异步 ReAct 循环，完美对接 DeepSeek/OpenAI 接口，将用户的自然语言实时转化为底层的 Tool Calling 指令。
* **🛠️ 协议服务中枢 (Server)**：基于 FastMCP 暴露本地能力。大模型可通过 MCP 协议直接“看懂”并调用本地的批处理函数，实现跨进程的安全调度。
* **👁️ 多格式解析器 (Parsers)**：内置 `txt` 和 `docx` 智能解析，支持一键读取包含表格的复杂 Word 文档。
* **✍️ 自动化生成器 (Writers)**：支持将大模型的结构化输出原样重组并持久化为新的 `.docx` 或 `.txt` 报告。

## 🚀 快速上手 (Quickstart)

### 1. 环境准备
确保您的环境中已安装 Python 3.8+。克隆项目后，安装核心依赖：
```bash
git clone [https://github.com/你的用户名/omnibatch-llm.git](https://github.com/你的用户名/omnibatch-llm.git)
cd omnibatch-llm
pip install -r requirements.txt
# 安装终端 UI 依赖
pip install rich mcp

```

### 2. 配置密钥

在项目根目录创建 `.env` 文件，并填入您的模型 API Key（默认配置为 DeepSeek）：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=[https://api.deepseek.com](https://api.deepseek.com)

```

### 3. 启动智能体控制台

1. 将需要处理的文件（`.txt` 或 `.docx`）放入 `data/inputs/` 目录。
2. 启动交互式终端：

```bash
python client/terminal_ui.py

```

3. 在控制台中输入您的自然语言指令，例如：

> *"提取 data/inputs 里面所有文档的核心观点，用一句话总结。"*

---

## 📝 更新日志 (Changelog)

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/) 规范。

### [v0.2.0] - 2026-03-16 (MCP 架构全面升级)

**🚀 Major (重大更新)**

* **架构重构**：全面迁移至 Model Context Protocol (MCP) 架构，拆分 Client 与 Server 端。
* **智能体终端**：新增 `client/terminal_ui.py`，采用 `rich` 库构建带有加载动画和 Markdown 渲染的极客控制台。
* **工具封装**：重构原有核心逻辑至 `core/workflow.py`，并作为标准的 MCP Tool 注册至 `server/mcp_server.py`。
* **动态意图识别**：彻底废弃静态的 `main.py` 脚本，现已支持 DeepSeek 动态识别用户意图并自动注入参数执行批处理。

### [v0.1.0] - 2026-03-15 (MVP 初始发布)

**🎉 Added (新增)**

* 构建项目核心骨架：`core`, `parsers`, `templates`, `writers`, `utils`。
* 支持 `.txt` 和 `.docx` 文档的自动化读写与大模型处理。

### [Unreleased] (开发中/待发布)

* **[Parsers]** 增加对 PDF 和 Markdown 文件的结构化解析插件。
* **[Writers]** 增加基于 JSON Schema 的强制结构化输出与校验功能，方便导出为 Excel 报表。
* **[Ecosystem]** 编写集成指南，支持将本项目的 Server 端直接接入 Cursor 或 Claude Desktop。

---

## 🤝 参与贡献 (Contributing)

欢迎任何形式的贡献！无论是提交 Issue 报告 Bug、增加新的文件解析器插件，还是优化 Prompt 模板，我们都非常期待您的 Pull Request。

## 📄 开源协议 (License)

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 协议开源。
