import os
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

class LLMEngine:
    """
    大语言模型交互核心引擎。
    默认配置为 DeepSeek，但由于采用 OpenAI 兼容格式，可轻松切换至 vLLM 等本地部署接口。
    """

    def __init__(self, model_name: str = "deepseek-chat"):
        # 从环境变量获取 API Key 和 Base URL
        # 如果没有配置 BASE_URL，则默认使用 DeepSeek 的官方接口
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
        self.model_name = model_name

        if not self.api_key:
            raise ValueError("未找到 LLM_API_KEY 环境变量，请在 .env 文件中配置。")

        # 初始化 OpenAI 客户端，但指向 DeepSeek (或 vLLM) 的地址
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate_response(self, prompt: str, system_prompt: str = "你是一个严谨的 AI 助手。") -> str:
        """
        发送 Prompt 并获取模型回复。
        内置了基础的异常捕获机制，防止批量任务因单次网络波动而中断。
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3, # 批量结构化处理任务建议调低 temperature 以保证输出稳定性
                max_tokens=4096
            )
            return response.choices[0].message.content.strip()

        except RateLimitError:
            # TODO: 后续迭代可在此处加入 tenacity 库实现指数退避重试
            print(f"警告: 触发 API 速率限制 (Rate Limit)。")
            return "ERROR: RATE_LIMIT"
        except APIConnectionError:
            print(f"错误: 网络连接失败，请检查你的网络或 BASE_URL。")
            return "ERROR: CONNECTION_FAILED"
        except APIError as e:
            print(f"错误: API 返回异常 - {str(e)}")
            return "ERROR: API_ERROR"
        except Exception as e:
            print(f"未知错误: {str(e)}")
            return "ERROR: UNKNOWN"