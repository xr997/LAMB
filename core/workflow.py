import os
import json
from typing import Dict, Any

from core.llm_engine import LLMEngine
from parsers.txt_parser import TxtParser
from parsers.docx_parser import DocxParser
from templates.prompt_loader import PromptLoader
from writers.txt_writer import TxtWriter
from writers.docx_writer import DocxWriter
from writers.csv_writer import CsvWriter  # <--- [新增] 导入 CSV Writer
from utils.file_ops import get_supported_files
import sys  # <--- [新增] 导入 sys 用于实时向终端输出
import re
from zipfile import BadZipFile # <--- [新增] 用于捕获假 docx 文件报错
from parsers.pdf_parser import PdfParser
def execute_batch_task(
    input_dir: str, 
    task_instruction: str, 
    task_mode: str = "mapping", # <--- [新增] 任务模式: "mapping" (1对1) 或 "aggregation" (多对1)
    output_dir: str = "./data/outputs", 
) -> str:
    """执行批量文档处理的核心工作流。"""
    
    if not os.path.exists(input_dir):
        return f"执行失败：找不到输入文件夹路径 {input_dir}"
    os.makedirs(output_dir, exist_ok=True)

    # 针对聚合任务，我们需要强制大模型输出 JSON 格式，方便提取字段填入表格
    if task_mode == "aggregation":
        dynamic_template = f"{task_instruction}\n\n请阅读以下文档，并严格以 JSON 格式输出结果（例如包含 '分数' 和 '评语' 字段）：\n<DOCUMENT>\n{{document_content}}\n</DOCUMENT>"
    else:
        dynamic_template = f"{task_instruction}\n\n请阅读并处理以下文档内容：\n<DOCUMENT>\n{{document_content}}\n</DOCUMENT>"
    
    try:
        engine = LLMEngine()
        loader = PromptLoader(default_template=dynamic_template)
    except Exception as e:
        return f"系统初始化失败：{str(e)}"

    files_to_process = get_supported_files(input_dir)
    if not files_to_process:
        return f"任务终止：在 {input_dir} 中未找到文档。"

    stats = {"total": len(files_to_process), "success": 0, "failed": 0, "errors": []}
    
    # [新增] 用于存储聚合任务的全局列表
    aggregated_results = []

    for file_path in files_to_process:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # [新增] 实时播报：正在阅读
        print(f"  📖 正在读取文件: {filename} ...", file=sys.stderr)
        
        try:
            # 强拦截旧版 .doc 文件
            

            # ---> 【修改开始】增加对 PDF 的分流逻辑 <---
            if ext == '.txt':
                parser = TxtParser()
            elif ext == '.docx':
                parser = DocxParser()
            elif ext == '.pdf':
                parser = PdfParser()
            else:
                continue # 如果是其他奇奇怪怪的文件，直接跳过

            document_text = parser.extract_text(file_path)
            if not document_text:
                raise ValueError("文件内容为空")
                
            # [新增] 实时播报：交由大模型处理
            print(f"  🧠 正在呼叫大模型分析: {filename} ...", file=sys.stderr)
                
            final_prompt = loader.build_prompt(document_content=document_text)
            result_text = engine.generate_response(prompt=final_prompt)
            
            if result_text.startswith("ERROR:"):
                raise RuntimeError(f"API 请求失败: {result_text}")

            # --- 核心分流逻辑 ---
            if task_mode == "aggregation":
                json_match = re.search(r'\{[\s\S]*\}', result_text)
                if json_match:
                    clean_json = json_match.group(0)
                    try:
                        parsed_data = json.loads(clean_json)
                        parsed_data["文件名"] = filename 
                        aggregated_results.append(parsed_data)
                        stats["success"] += 1
                        # [新增] 实时播报：聚合成功
                        print(f"  ✅ 成功提取结构化数据: {filename}", file=sys.stderr)
                    except json.JSONDecodeError:
                        raise ValueError("模型返回的内容无法被解析为合法 JSON")
                else:
                    raise ValueError("模型未返回任何包含 JSON 结构的回复")
            
            else:
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}_processed.docx")
                success = DocxWriter().save_result(content=result_text, output_path=output_path)
                if success:
                    stats["success"] += 1
                    # [新增] 实时播报：保存成功
                    print(f"  ✅ 成功保存新文件: {base_name}_processed.docx", file=sys.stderr)
                else:
                    raise IOError("文件保存失败")
                    
        except BadZipFile:
            stats["failed"] += 1
            error_msg = f"文件损坏 (可能是直接修改后缀名导致的假 .docx)"
            stats["errors"].append(f"{filename}: {error_msg}")
            print(f"  ❌ 跳过 {filename}: {error_msg}", file=sys.stderr)
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(f"{filename}: {str(e)}")
            print(f"  ❌ 处理 {filename} 失败: {str(e)}", file=sys.stderr)
                    
       

    # 循环结束后，如果是聚合模式，一次性把所有数据写入表格
    if task_mode == "aggregation" and aggregated_results:
        csv_path = os.path.join(output_dir, "batch_report.csv")
        CsvWriter().save_result(content=aggregated_results, output_path=csv_path)

    # 生成报告
    report = f"✅ 批量任务执行完毕。模式: {task_mode}\n📊 共发现 {stats['total']} 个文件，成功 {stats['success']} 个，失败 {stats['failed']} 个。"
    if stats["errors"]:
        report += "\n❌ 错误明细：\n" + "\n".join(f"  - {err}" for err in stats["errors"][:5])
    return report

def synthesize_multiple_papers(input_dir: str, user_question: str) -> str:
    """
    Map-Reduce 多文档综合问答流水线。
    先带着问题精读每篇文档 (Map)，再把提取到的核心信息汇总回答 (Reduce)。
    """
    if not os.path.exists(input_dir):
        return f"错误：找不到目录 {input_dir}"
        
    files_to_process = get_supported_files(input_dir)
    if not files_to_process:
        return "目录中没有支持的文档。"

    engine = LLMEngine()
    loader = PromptLoader()
    
    print(f"\n  [Map 阶段] 正在扫描 {len(files_to_process)} 份文档，寻找与 '{user_question}' 相关的线索...", file=sys.stderr)
    
    # ----------------------------------------
    # Step 1: Map 阶段 (带着问题读单篇)
    # ----------------------------------------
    intermediate_summaries = []
    
    # Map 阶段的 Prompt：极其关键的“目标前置”
    map_prompt_template = (
        "用户的核心问题是：【{user_question}】\n\n"
        "请阅读以下文献内容，提取所有能回答该问题的相关事实、数据或结论。\n"
        "如果该文献与问题完全无关，请只输出四个字：'无相关信息'。\n"
        "请尽量保持客观和精简。\n\n"
        "<DOCUMENT>\n{document_content}\n</DOCUMENT>"
    )

    for file_path in files_to_process:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        print(f"    📖 正在检索: {filename} ...", file=sys.stderr)
        
        try:
            if ext == '.txt': parser = TxtParser()
            elif ext in ['.doc', '.docx']: parser = DocxParser()
            elif ext == '.pdf': 
                from parsers.pdf_parser import PdfParser
                parser = PdfParser()
            else: continue
                
            document_text = parser.extract_text(file_path)
            if not document_text: continue
            
            # 组装单篇阅读 prompt
            loader.template = map_prompt_template
            map_prompt = loader.build_prompt(user_question=user_question, document_content=document_text)
            map_result = engine.generate_response(prompt=map_prompt)
            
            # 过滤掉无关文献，保留有效信息的“中间态”
            if "无相关信息" not in map_result and "ERROR:" not in map_result:
                # 强制溯源：绑定文件名
                intermediate_summaries.append(f"### 来源文献：{filename}\n{map_result}\n")
                print(f"    💡 发现线索: {filename}", file=sys.stderr)
                
        except Exception as e:
            print(f"    ❌ 读取 {filename} 失败: {str(e)}", file=sys.stderr)

    # ----------------------------------------
    # Step 2: Reduce 阶段 (汇总并回答)
    # ----------------------------------------
    if not intermediate_summaries:
        return f"❌ 综合分析完毕。在所有提供的文献中，均未找到与“{user_question}”相关的信息。"

    print(f"\n  [Reduce 阶段] 已收集到 {len(intermediate_summaries)} 篇文献的线索，正在进行跨文献综合推演...", file=sys.stderr)
    
    # 将所有单篇总结拼接成一个大长文
    combined_context = "\n".join(intermediate_summaries)
    
    # Reduce 阶段的 Prompt：强调跨文献对比和溯源
    reduce_prompt = (
        f"你是一个严谨的学术助理。你需要基于以下多篇文献的提取片段，回答用户的最终问题。\n\n"
        f"用户问题：【{user_question}】\n\n"
        f"要求：\n"
        f"1. 综合分析：不要简单罗列，请提炼共识、对比差异。\n"
        f"2. 强制溯源：在陈述每一个关键观点时，必须在句末标注来源（如：'根据《xxx.pdf》的研究...'）。\n"
        f"3. 严禁幻觉：如果提供的片段中没有信息，请明确说明无法得出结论。\n\n"
        f"<EXTRACTED_FRAGMENTS>\n{combined_context}\n</EXTRACTED_FRAGMENTS>"
    )
    
    final_answer = engine.generate_response(prompt=reduce_prompt)
    print(f"  ✅ 综合推演完成！", file=sys.stderr)
    
    return f"🔍 **跨文献综合分析报告**\n\n{final_answer}"