# LAMB

**本地优先、安全可信的多文档 AI 批处理与研究助理**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-lamb-orange)](#快速演示)
[![Safety](https://img.shields.io/badge/Safety-Prompt%20Injection%20Aware-red)](docs/security-model.md)

英文版：[README.md](README.md)

> 把一个资料夹交给 LAMB：扫描、解析、安全检查、分块、调用大模型、导出结果，并留下可审计记录。

---

## 为什么需要 LAMB

网页端 AI 工具适合处理单个文件，但面对一个资料夹时，常见问题会很快暴露：

| 痛点 | 常见结果 | LAMB 的解决方式 |
| --- | --- | --- |
| 文件太多 | 一个个上传，容易漏文件 | 本地扫描资料夹，批量处理支持格式文件 |
| 文档太长 | 超出上下文，回答不稳定 | 自动分块，再进行汇总推理 |
| 输出难整理 | 需要手工复制到表格或报告 | 直接导出 Markdown、CSV、JSON、DOCX |
| 结果不可追溯 | 不知道处理了哪些文件、哪些失败 | 每次运行生成 `manifest.json` 审计清单 |
| 文档内可能有恶意指令 | Prompt 注入可能诱导模型越权 | 将文档视为不可信证据，检测并记录风险 |

LAMB 的目标不是再做一个聊天界面，而是把“整个本地资料夹”变成一条可复现、可审计、可复用的 LLM 文档工作流。

---

## LAMB 能做什么

```text
资料夹
  -> 扫描文件
  -> 解析文本
  -> 安全检查
  -> 长文档分块
  -> LLM 批处理 / 多文档问答 / 字段抽取
  -> 导出结果
  -> 生成审计清单
```

### 核心能力

- **多文档研究问答**：跨论文、报告、会议纪要、课程材料提问，生成带来源引用的 Markdown 报告。
- **批量文档处理**：对每份文档执行摘要、翻译、润色、审阅、批改等任务。
- **结构化字段抽取**：从作业、简历、会议纪要、调研报告中抽取字段，输出 CSV 或 JSON。
- **安全可信处理**：检测 Prompt 注入，支持敏感信息脱敏，严格模式下跳过高风险文档。
- **长文档分块处理**：自动切分长文档，降低上下文超限风险。
- **可安装、可引用、可执行**：既能作为 Python 库被第三方程序引用，也能通过 `lamb` 命令运行。

---

## 日常应用场景

| 场景 | 示例命令 | 输出 |
| --- | --- | --- |
| 批量批改作业 | `lamb extract homework --fields "姓名,分数,评语,主要问题"` | CSV 批改表 |
| 批量阅读论文 | `lamb research papers --question "这些论文的方法有什么异同？"` | 带来源引用的综述报告 |
| 整理会议纪要 | `lamb extract meetings --fields "议题,待办,负责人,截止时间"` | 待办事项表 |
| 筛选简历 | `lamb extract resumes --fields "姓名,教育背景,技能,项目经验"` | 候选人信息表 |
| 汇总调研报告 | `lamb research reports --question "这些报告共同反映了什么趋势？"` | 跨文档总结 |
| 安全预览 | `lamb research docs --question "这些文档说了什么？" --dry-run` | 不调用模型的执行预览 |

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
```

扫描资料夹：

```bash
lamb scan data/inputs
```

跨文档提问：

```bash
lamb research data/inputs --question "这些文档的共同结论是什么？"
```

批量批改作业并导出表格：

```bash
lamb extract data/inputs --fields "姓名,分数,评语,主要问题" --redact
```

为每份文档生成摘要：

```bash
lamb batch data/inputs --instruction "请为这份文档写一段 200 字摘要" --format md
```

不调用大模型，只预览执行计划：

```bash
lamb research data/inputs --question "这些文档主要讨论了什么？" --dry-run
```

---

## Python 调用

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

## 安全模型

LAMB 的安全重点不是传统通信加密，而是面向真实文档工作流的 **LLM 应用层安全**。

- 文档内容会被包裹为 `<UNTRUSTED_DOCUMENT>`，只作为证据，不作为指令来源。
- Prompt 构造会明确禁止模型执行文档内部的反向指令。
- 内置 Prompt 注入检测，识别忽略系统指令、泄露系统提示、读取密钥、调用工具等风险。
- `--strict-security` 会跳过高风险文档。
- `--redact` 会脱敏邮箱、手机号、API key、token、JWT 类字符串。
- 默认跳过隐藏文件、`.env`、凭据类文件和符号链接。
- 每次运行都会生成审计清单，记录输入、输出、参数、风险提示、失败原因和耗时。

更多细节见 [docs/security-model.md](docs/security-model.md)。

---

## 输出物

LAMB 会根据工作流生成：

- Markdown 研究报告
- CSV 或 JSON 字段抽取表
- 每份文档对应的 Markdown、TXT 或 DOCX 结果
- `*_manifest.json` 审计清单

---

## 系统框架图

![LAMB 系统框架图](docs/assets/lamb-system-overview.png)

---

## 文档

- [快速上手](docs/quickstart.md)
- [Python API](docs/api.md)
- [示例场景](docs/examples.md)
- [安全模型](docs/security-model.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

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
