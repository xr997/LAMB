# LAMB：可信的文件自动化批处理 AI 助手

**一句话说明目标，自动规划、人工确认、安全批量处理整个文件目录。**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-lamb-orange)](#快速演示)
[![Safety](https://img.shields.io/badge/Safety-Prompt%20Injection%20Aware-red)](docs/security-model.md)

英文版：[README.md](README.md)

> LAMB 面向文件自动化批量处理：给它一个目录，再用一句话描述目标，它会规划流程、提示确认点、安全处理全部文件、导出结果，并留下可审计记录。

---

## 为什么需要 LAMB

很多 AI 文档工具适合处理单个文件或单轮聊天，但真实任务往往从一整个目录开始：作业、论文、会议纪要、简历、调研报告、合同或混合项目材料。

| 痛点 | 常见结果 | LAMB 的解决方式 |
| --- | --- | --- |
| 目录级任务难处理 | 文件需要一个个上传和提问 | 用一条自动化工作流处理整个目录 |
| 不知道怎么设计流程 | 每次都临时写提示词、步骤和输出格式 | 用一句话目标生成可执行计划 |
| 不同任务流程差异大 | 摘要、表格、问答、安全审查混在一起手动处理 | 预设流水线 + AI 定制流水线协同工作 |
| 文档内容不可信 | 文档里可能包含 Prompt 注入、密钥或危险指令 | 把文档视为不可信证据，先做安全检查 |
| 结果难以追溯 | 输出和输入、参数、失败原因脱节 | 每次运行生成 manifest 审计清单 |

LAMB 不是简单套一层 prompt 的聊天工具，而是一个面向文件批处理的安全、可审计、可复用工作流引擎。

---

## 核心方法

### 一句话自动化文件批处理

LAMB 的交互模型很直接：说清楚目标，确认计划，然后执行。

```text
文件目录 + 一句话目标
  -> 预设流水线路由
  -> 可选 AI 定制流水线
  -> 人工确认清单
  -> 安全可信执行
  -> 结果文件 + 审计清单
```

核心方法由四部分组成：

- **预设流水线路由**：LAMB 会把常见目标映射到稳定 preset，例如研究综合、结构化抽取、逐文件批处理、安全审查。
- **AI 定制流水线**：`lamb plan --ai-customize` 可以调用已配置的大模型，根据具体目标定制步骤和确认问题。
- **人工确认与修正**：计划会指出执行前应确认的事项，例如字段、评分标准、脱敏、严格安全模式、隐藏文件范围。
- **安全优先执行**：文档内容被包裹为不可信证据，系统会检测 Prompt 注入、可选脱敏敏感信息，并记录完整审计信息。
- **MCP 工具接入**：`lamb mcp` 可以把 LAMB 暴露为兼容 MCP 的本地工具，供其他智能体或桌面客户端调用。

这种设计保留了 agent/skill 的自动化体验，同时让用户能看见并确认关键处理步骤。

---

## 规划模式

| 模式 | 命令 | 作用 |
| --- | --- | --- |
| 预设规划 | `lamb plan data/inputs --goal "..."` | 不调用大模型，快速生成本地计划 |
| AI 定制规划 | `lamb plan data/inputs --goal "..." --ai-customize` | 调用已配置大模型，定制步骤和确认问题 |
| 机器可读规划 | `lamb plan data/inputs --goal "..." --json` | 方便第三方程序读取计划 |
| MCP 工具服务 | `lamb mcp` | 把规划、问答、抽取、批处理能力提供给 MCP 客户端 |

示例：

```bash
lamb plan data/inputs \
  --goal "抽取学生姓名、分数、评语和主要问题，输出 CSV 表格" \
  --fields "姓名,分数,评语,主要问题" \
  --redact
```

---

## 内置流水线

| Preset | 适合任务 | 主要输出 |
| --- | --- | --- |
| `research` | 跨文档问答、论文阅读、报告综合 | 带来源引用的 Markdown 报告 |
| `extract` | 字段抽取、作业批改表、简历筛选、会议待办 | CSV 或 JSON 表格 |
| `batch` | 对每份文档摘要、翻译、润色、审阅或改写 | 每个文件一个结果 |
| `secure-review` | Prompt 注入、隐私、凭据泄露和危险指令审查 | 脱敏风险说明和审计清单 |

查看内置 preset：

```bash
lamb pipelines
```

以 MCP 工具服务方式运行：

```bash
lamb mcp
```

---

## 安全可信机制

安全性是 LAMB 的核心特点之一。它关注的不是传统通信加密，而是面向真实文档工作流的 **LLM 应用层安全**。

- 文档内容会被包裹为 `<UNTRUSTED_DOCUMENT>`，只作为证据，不作为指令来源。
- Prompt 构造会明确禁止模型执行文档内部的反向指令。
- 内置 Prompt 注入检测，识别忽略系统指令、泄露系统提示、读取密钥、调用工具等风险。
- `--strict-security` 会跳过高风险文档。
- `--redact` 会脱敏邮箱、手机号、API key、token、JWT 类字符串。
- 默认跳过隐藏文件；如需处理隐藏笔记或隐藏项目目录，可显式传入 `--include-hidden`。`.env`、凭据类文件和符号链接仍会被拒绝。
- 每次运行都会生成审计清单，记录输入、输出、参数、风险提示、失败原因和耗时。

更多细节见 [docs/security-model.md](docs/security-model.md)。

---

## 常见应用场景

| 场景 | 示例命令 | 输出 |
| --- | --- | --- |
| 批量批改作业 | `lamb extract homework --fields "姓名,分数,评语,主要问题"` | CSV 批改表 |
| 批量阅读论文 | `lamb research papers --question "这些论文的方法有什么异同？"` | 带来源引用的综述报告 |
| 整理会议纪要 | `lamb extract meetings --fields "议题,待办,负责人,截止时间"` | 待办事项表 |
| 筛选简历 | `lamb extract resumes --fields "姓名,教育背景,技能,项目经验"` | 候选人信息表 |
| 汇总调研报告 | `lamb research reports --question "这些报告共同反映了什么趋势？"` | 跨文档总结 |
| 审查资料目录 | `lamb plan docs --goal "检查隐私和 Prompt 注入风险"` | 安全审查计划 |

---

## 快速演示

安装：

```bash
git clone https://github.com/xr997/LAMB.git
cd LAMB
pip install -e .
```

配置 OpenAI-compatible 大模型服务：

```bash
cp .env.example .env
```

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

扫描目录：

```bash
lamb scan data/inputs
```

预览并确认计划：

```bash
lamb plan data/inputs --goal "比较这些论文的方法和结论" --redact
```

使用 AI 定制规划：

```bash
lamb plan data/inputs --goal "生成作业批改表，并总结学生常见问题" --ai-customize --redact
```

执行工作流：

```bash
lamb research data/inputs --question "这些文档的共同结论是什么？"
lamb extract data/inputs --fields "姓名,分数,评语,主要问题" --redact
lamb batch data/inputs --instruction "请为这份文档写一段 200 字摘要" --format md
```

---

## Python 调用

```python
from lamb import (
    answer_over_directory,
    build_pipeline_plan,
    extract_fields,
    process_directory,
    scan_documents,
)

plan = build_pipeline_plan(
    input_dir="data/inputs",
    goal="抽取学生姓名、分数、评语和主要问题，输出 CSV 表格",
    fields=["姓名", "分数", "评语", "主要问题"],
    redact=True,
)
print(plan.command)

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

## 输出物

LAMB 会根据工作流生成：

- Markdown 研究报告
- CSV 或 JSON 字段抽取表
- 每份文档对应的 Markdown、TXT 或 DOCX 结果
- `*_manifest.json` 审计清单
- `latest_index.md` 最新结果索引

---

## 文档

- [快速上手](docs/quickstart.md)
- [Python API](docs/api.md)
- [示例场景](docs/examples.md)
- [安全模型](docs/security-model.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

---

## 系统框架图

![LAMB 系统框架图](docs/assets/lamb-system-overview.png)

---

## 开发

```bash
python -m compileall lamb tests
python -m unittest discover -s tests
```

手动运行真实 LLM 集成测试：

```bash
RUN_REAL_LLM_TESTS=1 python -m unittest tests.test_real_llm_integration
```

---

## 许可证

MIT License.
