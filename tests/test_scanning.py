import tempfile
import unittest
from pathlib import Path

from lamb.scanning import scan_documents, summarize_scan


class ScanningTests(unittest.TestCase):
    def test_scan_supported_and_skipped_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "paper.txt").write_text("hello", encoding="utf-8")
            (root / ".env").write_text("LLM_API_KEY=secret", encoding="utf-8")
            (root / "image.png").write_bytes(b"png")

            records = scan_documents(str(root))
            summary = summarize_scan(records)

            self.assertEqual(summary["total"], 3)
            self.assertEqual(summary["supported"], 1)
            self.assertEqual(summary["skipped"], 2)
            reasons = {record.relative_path: record.skip_reason for record in records}
            self.assertIn("sensitive", reasons[".env"])
            self.assertIn("unsupported", reasons["image.png"])


if __name__ == "__main__":
    unittest.main()
