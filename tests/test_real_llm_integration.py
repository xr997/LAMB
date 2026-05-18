import os
import tempfile
import unittest
from pathlib import Path

from dotenv import load_dotenv

from lamb.workflow import answer_over_directory, extract_fields, process_directory


load_dotenv(".env")


@unittest.skipUnless(
    os.getenv("RUN_REAL_LLM_TESTS") == "1" and os.getenv("LLM_API_KEY"),
    "set RUN_REAL_LLM_TESTS=1 and LLM_API_KEY to run real LLM integration tests",
)
class RealLLMIntegrationTests(unittest.TestCase):
    def test_research_extract_and_batch_with_real_llm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            inputs.mkdir()
            (inputs / "homework.txt").write_text(
                "学生：张三\n作业主题：阅读《乡土中国》第一章。\n内容：能说明差序格局，但例子较少。",
                encoding="utf-8",
            )
            (inputs / "paper_note.txt").write_text(
                "论文笔记：长文档问答可以先分块，再汇总证据。优点是降低上下文超限风险。",
                encoding="utf-8",
            )

            research = answer_over_directory(
                str(inputs),
                question="这两份文档分别讨论了什么？",
                output_dir=str(outputs),
                max_chars=2000,
            )
            self.assertTrue(research.ok)
            self.assertEqual(len(research.sources), 2)
            self.assertTrue(Path(research.report_path).exists())
            self.assertTrue(Path(research.manifest_path).exists())

            extraction = extract_fields(
                str(inputs),
                fields=["文档类型", "主题", "主要问题"],
                output_dir=str(outputs),
                max_chars=2000,
            )
            self.assertTrue(extraction.ok)
            self.assertEqual(len(extraction.rows), 2)
            self.assertTrue(Path(extraction.output_path).exists())

            batch = process_directory(
                str(inputs),
                instruction="请用一句话总结这份文档。",
                output_dir=str(outputs),
                output_format="md",
                max_chars=2000,
            )
            self.assertTrue(batch.ok)
            self.assertEqual(batch.succeeded, 2)
            self.assertTrue(all(result.output_path for result in batch.files if result.success))


if __name__ == "__main__":
    unittest.main()
