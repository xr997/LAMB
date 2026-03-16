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
@mcp.tool()
def auto_process_documents(input_dir: str, task_instruction: str) -> str:
    """
    当用户需要批量处理本地文档、批量批改作业、或者对文件夹中的文件进行结构化信息提取时调用此工具。
    
    Args:
        input_dir: 包含待处理文件的本地目标文件夹绝对或相对路径（例如: "./data/inputs"）。
        task_instruction: 用户期望大模型对这些文档执行的具体指令（例如: "批改作业并严格打分", "提取每篇论文的核心创新点"）。
        
    Returns:
        一段包含处理成功数量、失败数量以及错误明细的执行报告。
    """
    # 打印日志到标准错误输出 (stderr)，因为标准输出 (stdout) 被 MCP 的通信协议占用了
    print(f"[Server 端日志] 收到大模型指令，开始执行任务: {task_instruction}", file=sys.stderr)
    print(f"[Server 端日志] 目标文件夹: {input_dir}", file=sys.stderr)
    
    # 调用底层干活的 workflow
    try:
        report = execute_batch_task(
            input_dir=input_dir,
            task_instruction=task_instruction,
            output_dir="./data/outputs",  # 暂时硬编码输出路径，后续也可以作为参数暴露给大模型
            output_format=".docx"
        )
        print(f"[Server 端日志] 任务执行完毕，向大模型返回报告。", file=sys.stderr)
        return report
    except Exception as e:
        error_msg = f"工具执行发生致命错误: {str(e)}"
        print(f"[Server 端日志] {error_msg}", file=sys.stderr)
        return error_msg

if __name__ == "__main__":
    # 3. 启动服务器
    # transport='stdio' 表示通过标准输入/输出流与客户端(大模型)进行通信，这是 MCP 本地连接的标准做法
    mcp.run(transport='stdio')