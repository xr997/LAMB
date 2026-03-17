# 🚀 OmniBatch-LLM: 你的本地 AI 自动化批处理特工

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: MCP Agent](https://img.shields.io/badge/Architecture-MCP_Agent-purple.svg)](https://modelcontextprotocol.io/)

还在手动给大模型网页端一个个喂文件？或者为了调 API 熬夜手写各种 PDF/Word 解析脚本？

**OmniBatch-LLM** 是一个开箱即用的本地 AI 批处理框架。它完美填补了“网页端效率低下”与“纯写代码门槛过高”之间的空白。通过引入最前沿的 **MCP (Model Context Protocol) 智能体架构**，你只需在终端说一句话，它就能自动扫描你的本地文件夹、解析复杂文档、调度大模型完成批量任务，并生成排版精美的结构化报告。

**“Chat with your files” 已经落伍了，现在是 “Command your workflow” 的时代。**

---

## 🎯 为什么选择 OmniBatch-LLM？（直击痛点）

* ❌ **网页端 AI 的困境**：批量上传限制多、容易 Token 超限、输出结果只能手动复制粘贴，无法直接保存为原格式文件。
* ❌ **手写 API 脚本的噩梦**：需要自己折腾 `python-docx` 和 `PyMuPDF`、处理各种文件损坏报错、手动拼接 Prompt，扩展性极差。
* ✅ **OmniBatch 的终极解法**：
  * **零代码解析**：内置工业级解析器，自动搞定 `.txt`, `.docx`, `.pdf` 的文字提取与清洗。
  * **自然语言驱动**：无需修改代码，在极客风格的终端里用大白话下达指令（如：“帮我批改 inputs 文件夹里的作业”）。
  * **自动持久化**：处理结果自动保存为独立的新 `.docx` 文件，或者聚合成一张 `.csv` Excel 表格。

---

## 🔥 核心杀手级场景

无论是学术研究还是日常办公，OmniBatch-LLM 都能为你节省 90% 的机械劳动时间：

### 🎓 场景一：科研工作者的“超级学术助理”
* **文献批量综述**：“提取这 20 篇 PDF 论文的核心创新点和实验 Baseline，汇总成一个表格。”
* **Map-Reduce 级跨文献问答**：“综合阅读整个目录的文献，回答‘目前对激活向量的控制有哪些主流方法’，并强制标注引用来源。”
* **单篇精读**：“帮我精读这篇长文，提炼作者的未来工作展望。”

### 👩‍🏫 场景二：教育工作者的“自动化批改引擎”
* **海量作业批改**：“根据我给定的标准，批改文件夹里的所有 Word 作业，给每份作业打分并写一句评语。”
* 自动聚合结果至 `batch_report.csv`，告别手动登分的痛苦。

### 💼 场景三：职场打工人的“效率外挂”
* **简历批量筛选**：“从这批 PDF 简历中筛选出有 3 年以上 Python 经验的候选人，并提取他们的联系方式。”
* **文档批量翻译/润色**：“把这些技术文档全部翻译成中文，保持专业术语准确，并存为新的 Word 文件。”

---

## 🧩 卓越的可扩展性 (Hackable Architecture)

本项目并非一个封闭的黑盒，而是为开发者精心设计的模块化乐高：

* **高度解耦的流水线**：分为 `Parsers` (解析), `Templates` (提示词组装), `LLM Engine` (网络请求), `Writers` (持久化输出) 四大独立模块。增加新格式支持只需 10 分钟。
* **原生 MCP 支持**：底层核心逻辑已被封装为标准 MCP Tools (`server/mcp_server.py`)。你不仅可以使用自带的酷炫终端，还可以将其直接接入 Cursor 或 Claude Desktop！
* **智能防崩溃机制**：遇到损坏或伪造后缀的文档（如假 `.docx`），底层会自动拦截并跳过，绝不中断整个批处理任务流。

---

## 🚀 3 分钟快速上手

### 1. 安装与配置
克隆项目并安装极其轻量的依赖（支持 Python 3.8+）：
```bash
git clone [https://github.com/你的用户名/omnibatch-llm.git](https://github.com/你的用户名/omnibatch-llm.git)
cd omnibatch-llm
pip install -r requirements.txt
```

在项目根目录新建 `.env` 文件，填入你的 API 密钥（默认完美兼容 DeepSeek 等极具性价比的模型）：
```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=[https://api.deepseek.com](https://api.deepseek.com)
```

### 2. 启动智能终端
只需将待处理文件扔进 `data/inputs` 文件夹，然后运行：
```bash
python client/terminal_ui.py
```

### 3. 下达你的指令
在弹出的高亮终端中，像吩咐人类助手一样输入指令：
> *"提取 data/inputs 里面所有 PDF 文档的核心结论，并汇总成表格。"*

端起咖啡，看着优美的进度条，等待结果出现在 `data/outputs` 文件夹中即可。

---

## 🤝 参与贡献
本项目正处于高速迭代期。如果你有好的想法（比如接入异步高并发调度、增加图片 OCR 支持），欢迎提交 Issue 或 Pull Request！我们期待与你一起打造最强的本地 AI 工具链。

## 📄 License
MIT License.

