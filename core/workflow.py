import os
from typing import Dict, Any

# 导入我们之前写好的核心组件
from core.llm_engine import LLMEngine
from parsers.txt_parser import TxtParser
from parsers.docx_parser import DocxParser
from templates.prompt_loader import PromptLoader
from writers.txt_writer import TxtWriter
from writers.docx_writer import DocxWriter
from utils.file_ops import get_supported_files

def execute_batch_task(
    input_dir: str, 
    task_instruction: str, 
    output_dir: str = "./data/outputs", 
    output_format: str = ".docx"
) -> str:
    """
    执行批量文档处理的核心工作流 (Skill / Tool)。
    
    Args:
        input_dir (str): 包含待处理文件的目标文件夹路径。
        task_instruction (str): 大模型（或用户）下达的具体任务指令，例如“批改作业并打分”。
        output_dir (str, optional): 结果保存路径。默认为 "./data/outputs"。
        output_format (str, optional): 结果保存格式。默认为 ".docx"。
        
    Returns:
        str: 任务执行结果的总结报告（供 MCP Server 返回给大模型）。
    """
    # 1. 基础校验与目录准备
    if not os.path.exists(input_dir):
        return f"执行失败：找不到输入文件夹路径 {input_dir}"
    os.makedirs(output_dir, exist_ok=True)

    # 2. 动态构建 Prompt 模板
    # 将用户的自然语言指令与我们要注入的文档内容合并
    dynamic_template = f"{task_instruction}\n\n请阅读并处理以下文档内容：\n<DOCUMENT>\n{{document_content}}\n</DOCUMENT>"
    
    try:
        engine = LLMEngine()
        loader = PromptLoader(default_template=dynamic_template)
    except Exception as e:
        return f"系统初始化失败：{str(e)}"

    # 3. 扫描文件
    files_to_process = get_supported_files(input_dir)
    if not files_to_process:
        return f"任务终止：在 {input_dir} 中未找到支持的文档格式（.txt, .docx）。"

    # 4. 初始化统计信息
    stats = {
        "total": len(files_to_process),
        "success": 0,
        "failed": 0,
        "errors": []
    }

    # 5. 执行处理循环 (静默执行，因为这是后端服务)
    for file_path in files_to_process:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            # 读文档
            if ext == '.txt':
                parser = TxtParser()
            elif ext in ['.doc', '.docx']:
                parser = DocxParser()
            else:
                continue
                
            document_text = parser.extract_text(file_path)
            if not document_text:
                stats["failed"] += 1
                stats["errors"].append(f"{filename}: 文件为空")
                continue
                
            # 组装 Prompt 并请求大模型
            final_prompt = loader.build_prompt(document_content=document_text)
            result_text = engine.generate_response(prompt=final_prompt)
            
            if result_text.startswith("ERROR:"):
                stats["failed"] += 1
                stats["errors"].append(f"{filename}: 模型 API 请求失败 ({result_text})")
                continue
                
            # 保存结果
            base_name = os.path.splitext(filename)[0]
            output_name = f"{base_name}_processed{output_format}"
            output_path = os.path.join(output_dir, output_name)
            
            writer = TxtWriter() if output_format == '.txt' else DocxWriter()
            success = writer.save_result(content=result_text, output_path=output_path)
            
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
                stats["errors"].append(f"{filename}: 文件保存失败")
                
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(f"{filename}: {str(e)}")

    # 6. 生成给大模型的执行报告
    report = (
        f"✅ 批量任务执行完毕。\n"
        f"📊 统计：共发现 {stats['total']} 个文件，成功处理 {stats['success']} 个，失败 {stats['failed']} 个。\n"
        f"📁 结果已保存至：{os.path.abspath(output_dir)}"
    )
    if stats["errors"]:
        report += "\n❌ 错误明细：\n" + "\n".join(f"  - {err}" for err in stats["errors"][:5])
        if len(stats["errors"]) > 5:
            report += f"\n  - ...(等共 {len(stats['errors'])} 个错误)"
            
    return report