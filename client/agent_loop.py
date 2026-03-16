import os
import sys
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

# 使用异步版本的 OpenAI 客户端，完美兼容异步的 MCP 协议
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

# MCP 官方客户端 SDK
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

class AgentContext:
    """
    智能体上下文与核心循环管理器。
    负责连接 MCP Server、转换工具格式、并与 DeepSeek 进行多轮交互。
    """
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
        
        if not api_key:
            raise ValueError("未找到 LLM_API_KEY 环境变量，请配置 .env 文件")
            
        # 初始化大模型客户端
        self.llm_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = "deepseek-chat"
        
        # 维护对话历史
        self.messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system", 
                "content": (
                    "你是一个强大的自动化办公与文档处理 AI 助手。你可以理解用户的意图，"
                    "并在需要时调用外部工具（Tools）来完成实际的批处理任务。"
                    "当你调用工具后，请向用户简明扼要地总结工具的执行结果。"
                )
            }
        ]

    async def chat_loop(self, user_input: str) -> str:
        """
        核心 Agent 循环：处理单次用户输入，并自动决定是否调用本地 MCP 工具。
        """
        self.messages.append({"role": "user", "content": user_input})

        # 1. 配置如何启动我们的 MCP Server (通过标准流 stdio)
        # sys.executable 指向当前的 python 解释器
        server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server", "mcp_server.py")
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env=None
        )

        # 2. 建立与 MCP Server 的连接
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化通信会话
                await session.initialize()
                
                # 3. 从本地 Server 获取它暴露出来的所有工具 (比如 auto_process_documents)
                mcp_tools_response = await session.list_tools()
                
                # 4. 将 MCP 的工具格式转换为 DeepSeek / OpenAI 能看懂的 Function Calling 格式
                available_tools = []
                for tool in mcp_tools_response.tools:
                    available_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    })

                # 5. 第 1 次发给大模型：带着用户的话和工具箱，问它怎么做
                response = await self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=self.messages,
                    tools=available_tools if available_tools else None,
                    temperature=0.3
                )
                
                response_message = response.choices[0].message
                self.messages.append(response_message) # 将大模型的思考加入历史

                # 6. 判断大模型是否决定调用工具
                if response_message.tool_calls:
                    # 它决定要干活了！遍历它想调用的所有工具
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # 核心动作：向 MCP Server 发起工具调用请求
                        try:
                            # 调用我们在 server/mcp_server.py 注册的函数
                            mcp_result = await session.call_tool(tool_name, tool_args)
                            
                            # 提取执行结果中的文本
                            result_text = "\n".join([content.text for content in mcp_result.content if content.type == "text"])
                        except Exception as e:
                            result_text = f"工具执行失败: {str(e)}"
                            
                        # 7. 将执行结果作为 'tool' 角色发回给大模型
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": result_text
                        })
                    
                    # 8. 第 2 次发给大模型：拿着工具执行的报告，让它给用户写个总结
                    final_response = await self.llm_client.chat.completions.create(
                        model=self.model_name,
                        messages=self.messages,
                        temperature=0.7
                    )
                    
                    final_text = final_response.choices[0].message.content
                    self.messages.append({"role": "assistant", "content": final_text})
                    return final_text
                    
                else:
                    # 大模型觉得不需要用工具（比如用户只是在闲聊），直接返回它的回答
                    return response_message.content or "无返回内容"