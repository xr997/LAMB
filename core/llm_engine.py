import os
import time
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

class LLMEngine:
    def __init__(self, model_name: str = "deepseek-chat"):
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
        self.model_name = model_name

        if not self.api_key:
            raise ValueError("未找到 LLM_API_KEY 环境变量，请在 .env 文件中配置。")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_response(self, prompt: str, system_prompt: str = "你是一个严谨的 AI 助手。", max_retries: int = 3) -> str:
        """带有指数退避重试机制的大模型请求函数。"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 重试循环
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.1,  # 调低随机性，确保结构化输出极其稳定
                    max_tokens=4096
                )
                return response.choices[0].message.content.strip()

            except RateLimitError:
                wait_time = (attempt + 1) * 3  # 依次等待 3秒, 6秒, 9秒
                print(f"    ⏳ 触发限流，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            except APIConnectionError:
                print(f"    🔌 网络波动，2秒后重试连接...")
                time.sleep(2)
            except APIError as e:
                return f"ERROR: API 发生内部错误 - {str(e)}"
            except Exception as e:
                return f"ERROR: 发生未知错误 - {str(e)}"
                
        return "ERROR: 超过最大重试次数，请求失败"