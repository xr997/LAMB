import json
import tempfile
import unittest
from pathlib import Path

from lamb.workflow import answer_over_directory, extract_fields, process_directory


class FakeLLM:
    model_name = "fake-test-model"

    def __init__(self):
        self.prompts = []

    def generate(self, prompt, system_prompt=None):
        self.prompts.append(prompt)
        if "Return exactly one JSON object" in prompt:
            return json.dumps({"姓名": "张三", "分数": "95", "评语": "结构清楚"}, ensure_ascii=False)
        if "Write a Markdown research report" in prompt:
            return "# 结论摘要\n这些文档都讨论了学习计划。"
        return "chunk result with source"


class WorkflowTests(unittest.TestCase):
    def test_batch_dry_run_writes_manifest_and_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            inputs.mkdir()
            (inputs / "a.txt").write_text("第一份作业内容", encoding="utf-8")

            result = process_directory(
                str(inputs),
                instruction="请给出简短评语",
                output_dir=str(outputs),
                output_format="md",
                dry_run=True,
            )

            self.assertEqual(result.succeeded, 1)
            self.assertTrue(Path(result.manifest_path).exists())
            self.assertTrue(Path(result.files[0].output_path).exists())

    def test_research_with_fake_llm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            inputs.mkdir()
            (inputs / "paper.md").write_text("# Paper\n研究方法是对比实验。", encoding="utf-8")

            result = answer_over_directory(
                str(inputs),
                question="研究方法是什么？",
                output_dir=str(outputs),
                llm_client=FakeLLM(),
            )

            self.assertIn("结论摘要", result.answer)
            self.assertEqual(result.sources, ["paper.md"])
            self.assertTrue(Path(result.report_path).exists())

    def test_extract_fields_with_fake_llm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            inputs.mkdir()
            (inputs / "homework.txt").write_text("姓名：张三\n内容：作业完成较好", encoding="utf-8")

            result = extract_fields(
                str(inputs),
                fields=["姓名", "分数", "评语"],
                output_dir=str(outputs),
                llm_client=FakeLLM(),
            )

            self.assertEqual(result.rows[0]["姓名"], "张三")
            self.assertTrue(Path(result.output_path).exists())
            self.assertTrue(Path(result.manifest_path).exists())


if __name__ == "__main__":
    unittest.main()
