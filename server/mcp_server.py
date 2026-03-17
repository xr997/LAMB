import sys
import os
from dotenv import load_dotenv  # <--- [新增] 导入 dotenv
# 将项目根目录加入系统路径，确保能正确导入 core 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()
from mcp.server.fastmcp import FastMCP
from core.workflow import execute_batch_task

# 1. 初始化 FastMCP 服务器实例
# "OmniBatch" 是这个服务器的名字，当外部客户端连接时会看到这个名字
mcp = FastMCP("OmniBatch")

# 2. 注册 Tool (工具/技能)
# @mcp.tool() 装饰器会自动将下面这个 Python 函数转化为标准的 MCP Tool 接口。
# 【关键】大模型就是通过阅读下面的函数名、类型注解和 docstring(多行注释) 来决定是否调用它的！
# ... 保持其他引用不变 ...

@mcp.tool()
def auto_process_documents(input_dir: str, task_instruction: str, task_mode: str = "mapping") -> str:
    """
    当用户需要处理本地文档时调用此工具。
    
    Args:
        input_dir: 包含待处理文件的本地目标文件夹路径。
        task_instruction: 具体的执行指令。
        task_mode: 任务模式。
                   如果是"翻译"、"摘要"等需要逐个输出新文件的任务，必须传入 "mapping"。
                   如果是"批改作业"、"信息抽取"等需要把所有结果汇总到一个 Excel 表格的任务，必须传入 "aggregation"。
    """
    print(f"[Server] 指令: {task_instruction} | 模式: {task_mode}", file=sys.stderr)
    
    try:
        return execute_batch_task(
            input_dir=input_dir,
            task_instruction=task_instruction,
            task_mode=task_mode
        )
    except Exception as e:
        return f"工具执行发生致命错误: {str(e)}"
# 导入我们新写的函数
from core.workflow import execute_batch_task, process_single_document, synthesize_multiple_papers

# ...保留其他的 tools...

@mcp.tool()
def multi_paper_qa(input_dir: str, user_question: str) -> str:
    """
    当用户需要你基于整个文件夹里的“多篇论文”进行对比、总结、或回答特定问题时，调用此工具。
    这是一个高级的高成本工具，它会先阅读所有文献，再进行综合解答。
    
    Args:
        input_dir: 包含论文的目录路径（例如: "data/inputs"）。
        user_question: 用户的核心问题或综述指令（例如: "各篇论文在数据预处理上有什么不同？"）。
    """
    print(f"[Server] 启动多文献 Map-Reduce 综合分析 | 目标问题: {user_question}", file=sys.stderr)
    return synthesize_multiple_papers(input_dir, user_question)
    
if __name__ == "__main__":
    # 3. 启动服务器
    # transport='stdio' 表示通过标准输入/输出流与客户端(大模型)进行通信，这是 MCP 本地连接的标准做法
    mcp.run(transport='stdio')