"""LLM client abstraction for production and tests."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class LLMClient(Protocol):
    model_name: str

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        ...


@dataclass
class OpenAIChatClient:
    """Small OpenAI-compatible chat client."""

    model_name: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.1
    max_tokens: int = 4096
    max_retries: int = 5
    timeout: float = 90.0

    def __post_init__(self) -> None:
        try:
            from dotenv import load_dotenv

            load_dotenv(Path.cwd() / ".env")
        except ImportError:
            pass
        self.model_name = self.model_name or os.getenv("LLM_MODEL", "deepseek-chat")
        self.api_key = self.api_key or os.getenv("LLM_API_KEY")
        self.base_url = self.base_url or os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
        if not self.api_key:
            raise ValueError("LLM_API_KEY is required unless dry-run mode or a custom LLM client is used")
        from openai import OpenAI

        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

        messages = [
            {"role": "system", "content": system_prompt or "You are a careful document assistant."},
            {"role": "user", "content": prompt},
        ]
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                content = response.choices[0].message.content
                return (content or "").strip()
            except RateLimitError as exc:
                last_error = exc
                time.sleep(2 + attempt * 3)
            except (APIConnectionError, APITimeoutError) as exc:
                last_error = exc
                time.sleep(1 + attempt * 2)
            except APIError as exc:
                raise RuntimeError(f"LLM API error: {exc}") from exc
        detail = f": {last_error}" if last_error else ""
        raise RuntimeError(f"LLM API request failed after retries{detail}")


class DryRunClient:
    """Deterministic client used for dry-run previews and some tests."""

    model_name = "dry-run"

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        preview = prompt.strip().replace("\n", " ")
        if len(preview) > 240:
            preview = preview[:240] + "..."
        return f"[DRY RUN] LLM call skipped. Prompt preview: {preview}"
