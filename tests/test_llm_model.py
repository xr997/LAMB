import os
import unittest
from unittest.mock import patch

from lamb.cli import build_parser
from lamb.llm import OpenAIChatClient


class ModelSelectionTests(unittest.TestCase):
    def test_env_model_is_used_when_no_explicit_model(self):
        with patch.dict(os.environ, {"LLM_MODEL": "gpt-4o-mini"}, clear=False):
            client = OpenAIChatClient(api_key="test-key")
            self.assertEqual(client.model_name, "gpt-4o-mini")

    def test_explicit_model_overrides_env_model(self):
        with patch.dict(os.environ, {"LLM_MODEL": "gpt-4o-mini"}, clear=False):
            client = OpenAIChatClient(api_key="test-key", model_name="deepseek-chat")
            self.assertEqual(client.model_name, "deepseek-chat")

    def test_cli_accepts_model_argument(self):
        parser = build_parser()
        args = parser.parse_args(
            ["research", "data/inputs", "--question", "demo", "--model", "gpt-4o-mini", "--dry-run"]
        )
        self.assertEqual(args.model, "gpt-4o-mini")


if __name__ == "__main__":
    unittest.main()
