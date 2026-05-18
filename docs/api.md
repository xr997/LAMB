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
