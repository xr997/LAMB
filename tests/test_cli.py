import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from lamb.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_scan_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "note.txt").write_text("hello", encoding="utf-8")
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                exit_code = main(["scan", str(root)])
            self.assertEqual(exit_code, 0)

    def test_pipelines_command(self):
        stdout = StringIO()
        with redirect_stdout(stdout), redirect_stderr(StringIO()):
            exit_code = main(["pipelines"])
        self.assertEqual(exit_code, 0)
        self.assertIn("research", stdout.getvalue())
        self.assertIn("secure-review", stdout.getvalue())

    def test_help_lists_mcp_command(self):
        self.assertIn("mcp", build_parser().format_help())

    def test_plan_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            inputs.mkdir()
            stdout = StringIO()
            with redirect_stdout(stdout), redirect_stderr(StringIO()):
                exit_code = main(
                    [
                        "plan",
                        str(inputs),
                        "--goal",
                        "抽取姓名、分数和评语，输出 CSV 表格",
                        "--fields",
                        "姓名,分数,评语",
                    ]
                )
            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Selected preset: extract", output)
            self.assertIn("--fields", output)

    def test_research_dry_run_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            inputs.mkdir()
            (inputs / "note.txt").write_text("hello", encoding="utf-8")
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                exit_code = main(
                    [
                        "research",
                        str(inputs),
                        "--question",
                        "这份资料说了什么？",
                        "--output-dir",
                        str(outputs),
                        "--dry-run",
                    ]
                )
            self.assertEqual(exit_code, 0)

    def test_batch_accepts_include_hidden_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            hidden = inputs / ".notes"
            hidden.mkdir(parents=True)
            (hidden / "note.txt").write_text("hidden note", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout), redirect_stderr(StringIO()):
                exit_code = main(
                    [
                        "batch",
                        str(inputs),
                        "--instruction",
                        "Summarize this note.",
                        "--output-dir",
                        str(outputs),
                        "--format",
                        "md",
                        "--dry-run",
                        "--include-hidden",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("succeeded: 1", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
