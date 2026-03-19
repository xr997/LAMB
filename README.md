# 🚀 LAMB
## LAMB: Lightweight Agent for Massive Batch-processing

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: MCP Agent](https://img.shields.io/badge/Architecture-MCP_Agent-purple.svg)](https://modelcontextprotocol.io/)

还在手动拖拽海量文件到 AI 网页端？还在为了调用一个 API 而熬夜手写复杂的 PDF/Word 解析脚本？

**LAMB** 是一个开箱即用的本地 AI 批处理框架，旨在为开发者和研究人员提供一个极简、极其便捷的文件自动化处理方案。它完美填补了“网页端手动处理效率低下”与“纯手写代码门槛过高”之间的空白。通过引入最前沿的 **MCP (Model Context Protocol) 智能体架构**，你只需在极客风格的终端里输入一句简单的指令，系统的大脑（如 DeepSeek）便会自动拆解意图、寻址本地文件夹、全自动解析文档、处理并生成结构化报告。

**告别机械式的拖拽与繁琐的代码配置，让 LAMB 接管你的海量文件流水线。**

---

## 🎯 核心卖点与痛点直击

* ❌ **网页端大模型 (ChatGPT/DeepSeek Web) 的痛点**：传文件太累、容易断线且Token超限，处理结果无法直接保存为本地原格式文件。
* ❌ **手动编写 API 脚本的痛点**：需要从头折腾 `python-docx` 和 `PyMuPDF`，需要自己处理损坏文件的报错，扩展性极差。
* ✅ **LAMB 的轻量级解法**：
  * **零配置解析**：内置工业级文件解析器，自动搞定 `.txt`, `.docx`, `.pdf` 的文字提取与清洗。
  * **指令驱动一切**：无需修改代码配置，在终端中用一句自然语言指令（如：“批改 data/inputs 里的作业”）即可驱动全流程。
  * **本地安全持久化**：处理结果自动保存为独立的新 `.docx` 文件，或者聚合成一张 `.csv` Excel 报表，完全在本地安全运行。
  * **极致轻量便捷**：比起像龙虾（LangChain）一样庞大、复杂的 Agent 框架，LAMB 的配置极其简单、便捷，开箱即用。

---

## 🔥 核心应用场景示例

无论是学术研究还是自动化批改，LAMB 都能为你节省 90% 的机械劳动时间：

### 🎓 科研学术助理
* **Map-Reduce 级文献综合分析**：“综合阅读整个目录的文献，回答‘激活向量控制的主要方法有哪些’，并强制标注引用来源。”
* **单篇文献精准分析**：“帮我精读这篇长文，提炼作者的 linear probes 实验结果。”

### 👩‍🏫 自动化批改引擎
* **海量作业批量批改**：“根据给定的标准，批改文件夹里的所有 Word 作业，打分并写一句评语。”
* 聚合结果至 `batch_report.csv`，告别手动登分的痛苦。

---

## 🧩 模块化可扩展架构

* ** Parsers (解析)**：插件式设计，轻松增加新格式（如 PDF/MarkDown）支持。
* **Templates (提示词组装)**：让指令与代码逻辑完全解耦。
* **LLM Engine (网络请求)**：统一封装兼容 OpenAI 的大模型 API 调用。
* **Writers (持久化输出)**：支持将模型输出重组并持久化保存为各种格式文件。
* **MCP 支持**：底层核心已被封装为标准 MCP Tools。你可以使用本项目自带的控制台，也可以将其直接接入 Cursor 或 Claude Desktop！

---

## 🚀 3 分钟快速上手

### 1. 克隆与安装
```bash
git clone [https://github.com/你的用户名/lamb.git](https://github.com/你的用户名/lamb.git)
cd lamb
pip install -r requirements.txt
# 安装终端 UI 依赖
pip install rich mcp
```

### 2. 配置密钥
在项目根目录新建 `.env` 文件，填入你的 API 密钥（默认完美兼容 DeepSeek）：
```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=[https://api.deepseek.com](https://api.deepseek.com)
```

### 3. 启动智能终端
只需将待处理文件扔进 `data/inputs` 文件夹，然后运行：
```bash
python client/terminal_ui.py
```

在终端中像吩咐人类助手一样输入指令：
> *"提取 data/inputs 里面所有 PDF 论文的核心结论，并汇总成表格。"*

端起咖啡，看着优美的进度条，等待结果出现在 `data/outputs` 文件夹中即可。

---

## 📝 更新日志 (Changelog)

### [v0.3.0] - 2026-03-18 (品牌重构与功能整合)
**🎉 Rebranding (品牌重构)**
* 项目正式更名为 **LAMB** (**L**ightweight **A**gent for **M**assive **B**atch-processing)，强调极简轻量与海量批处理卖点。
**🚀 Added (新增)**
* 在 `core/workflow.py` 中引入高级 Map-Reduce 全流程流水线，支持对整个目录进行多文档综合问答。

### [v0.2.0] - 2026-03-16 (MCP Agent 架构全面升级)
* 全面迁移至 Model Context Protocol (MCP) 架构，拆分 Client 与 Server 端，引入异步 ReAct 智能体循环。

---

## 🤝 参与贡献
我们期待与你一起打造最强的本地 AI 工具链。

## 📄 License
MIT License.
