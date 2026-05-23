# Python API

LAMB can be used as a normal Python package after installation.

```bash
pip install -e .
```

## Scan Documents

```python
from lamb import scan_documents

records = scan_documents("data/inputs")
for record in records:
    print(record.relative_path, record.supported, record.skip_reason)
```

Set `include_hidden=True` when a workflow should process intentional hidden notes or project folders. Sensitive names such as `.env` are still refused.

## Pipeline Planning

```python
from lamb import build_pipeline_plan, customize_pipeline_plan, list_pipeline_presets, render_pipeline_plan
from lamb.llm import OpenAIChatClient

for preset in list_pipeline_presets():
    print(preset.name, preset.title)

plan = build_pipeline_plan(
    input_dir="data/inputs",
    goal="抽取学生姓名、分数、评语和主要问题，输出 CSV 表格",
    fields=["姓名", "分数", "评语", "主要问题"],
    redact=True,
)

print(plan.command)
print(render_pipeline_plan(plan))

customized = customize_pipeline_plan(plan, OpenAIChatClient())
print(render_pipeline_plan(customized))
```

Use pipeline planning when an application needs to preview or confirm a workflow before sending document content to an LLM. `build_pipeline_plan()` is local and deterministic; `customize_pipeline_plan()` calls the configured LLM to tailor the displayed steps and confirmation checklist.

## MCP Tool Server

Run LAMB as a local MCP server when another agent or desktop client should call its tools:

```bash
lamb mcp
```

The MCP server exposes planning, research QA, structured extraction, and per-document batch processing using the current `lamb` workflow implementation.

## Multi-document Research

```python
from lamb import answer_over_directory

result = answer_over_directory(
    input_dir="data/inputs",
    question="这些文档的共同结论是什么？",
    output_dir="data/outputs",
    redact=True,
    include_hidden=True,
)

print(result.answer)
print(result.report_path)
print(result.manifest_path)
```

## Structured Extraction

```python
from lamb import extract_fields

result = extract_fields(
    input_dir="data/inputs",
    fields=["姓名", "分数", "评语"],
    output_dir="data/outputs",
    include_hidden=True,
)

print(result.rows)
```

## Batch Processing

```python
from lamb import process_directory

result = process_directory(
    input_dir="data/inputs",
    instruction="请为每份文档生成摘要",
    output_format="md",
    include_hidden=True,
)

for file_result in result.files:
    print(file_result.success, file_result.output_path, file_result.message)
```

## Custom LLM Client

Tests and applications can inject their own LLM client. The object only needs a `model_name` attribute and a `generate(prompt, system_prompt=None)` method.

```python
class MyClient:
    model_name = "my-model"

    def generate(self, prompt, system_prompt=None):
        return "model output"

result = process_directory(
    "data/inputs",
    instruction="摘要",
    output_format="md",
    llm_client=MyClient(),
)
```
