import unittest

from lamb.chunking import estimate_tokens, split_text


class ChunkingTests(unittest.TestCase):
    def test_short_text_creates_single_chunk(self):
        chunks = split_text("hello world", "demo.txt", max_chars=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].label, "demo.txt#chunk-1-of-1")

    def test_long_text_creates_overlapping_chunks(self):
        text = "A" * 100 + "\n\n" + "B" * 100 + "\n\n" + "C" * 100
        chunks = split_text(text, "demo.txt", max_chars=120, overlap_chars=20)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0].index, 0)
        self.assertGreater(chunks[1].start_char, 0)

    def test_token_estimate_handles_cjk(self):
        self.assertGreater(estimate_tokens("这是一段中文文本"), 0)


if __name__ == "__main__":
    unittest.main()
