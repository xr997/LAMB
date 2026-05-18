import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from lamb.cli import main


class CliTests(unittest.TestCase):
    def test_scan_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "note.txt").write_text("hello", encoding="utf-8")
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                exit_code = main(["scan", str(root)])
            self.assertEqual(exit_code, 0)

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


if __name__ == "__main__":
    unittest.main()
