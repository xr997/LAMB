import tempfile
import unittest
from pathlib import Path

from lamb.workflow import process_directory


class OutputIndexTests(unittest.TestCase):
    def test_batch_writes_latest_output_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root / "inputs"
            outputs = root / "outputs"
            inputs.mkdir()
            (inputs / "note.txt").write_text("hello", encoding="utf-8")

            result = process_directory(
                str(inputs),
                instruction="summarize",
                output_dir=str(outputs),
                output_format="md",
                dry_run=True,
            )

            index_path = outputs / "latest_index.md"
            self.assertTrue(index_path.exists())
            content = index_path.read_text(encoding="utf-8")
            self.assertIn(result.run_id, content)
            self.assertIn("batch", content)
            self.assertIn(result.manifest_path, content)
            self.assertIn(result.files[0].output_path, content)


if __name__ == "__main__":
    unittest.main()
