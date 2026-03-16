import asyncio
import sys
import os

# 将项目根目录加入系统路径，确保能顺利导入同级模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
except ImportError:
    print("错误: 缺少终端美化库 'rich'。")
    print("请在终端运行: pip install rich")
    sys.exit(1)

# 导入我们刚刚写好的大脑
from client.agent_loop import AgentContext

async def main():
    console = Console()
    
    # 打印欢迎面板
    console.print(Panel.fit(
        "[bold cyan]🚀 OmniBatch-LLM 智能体控制台[/bold cyan]\n"
        "[dim]您现在可以通过自然语言直接指挥本地批处理工作流。[/dim]\n"
        "[dim]提示：输入 'exit' 或 'quit' 即可退出系统。[/dim]",
        border_style="cyan"
    ))

    # 初始化智能体
    try:
        with console.status("[bold green]正在唤醒 DeepSeek 大脑并准备 MCP 通信通道...[/bold green]"):
            agent = AgentContext()
        console.print("[bold green]✅ 系统初始化完毕！随时可以下达任务。[/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]❌ 初始化失败: {str(e)}[/bold red]")
        console.print("[yellow]请检查您的 .env 文件中是否正确配置了 LLM_API_KEY。[/yellow]")
        return

    # 核心对话循环
    while True:
        try:
            # 1. 获取用户输入
            user_input = Prompt.ask("[bold blue]🧑 您[/bold blue]")
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("\n[bold cyan]👋 任务结束，系统已安全关闭。期待下次为您服务！[/bold cyan]")
                break
                
            if not user_input.strip():
                continue

            # 2. 将输入交给 Agent 处理，并显示思考动画
            with console.status("[bold magenta]🤖 Agent 正在思考并调度底层工具... (文件越多耗时越长，请稍候)[/bold magenta]", spinner="dots"):
                response = await agent.chat_loop(user_input)
            
            # 3. 渲染大模型返回的 Markdown 结果
            console.print("\n[bold magenta]🤖 OmniBatch Agent[/bold magenta]")
            console.print(Panel(Markdown(response), border_style="magenta"))
            console.print() # 打印空行留白

        except KeyboardInterrupt:
            # 捕获 Ctrl+C 强制退出
            console.print("\n\n[bold cyan]👋 检测到中断指令，系统已安全关闭。[/bold cyan]")
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ 运行过程中发生未捕获的错误: {str(e)}[/bold red]")

if __name__ == "__main__":
    # 因为核心逻辑是异步的，所以需要用 asyncio.run 来启动程序
    asyncio.run(main())