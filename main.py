import os
from dotenv import load_dotenv

# 导入我们写好的各个模块
from core.llm_engine import LLMEngine
from parsers.txt_parser import TxtParser
from parsers.docx_parser import DocxParser
from templates.prompt_loader import PromptLoader
from writers.txt_writer import TxtWriter
from writers.docx_writer import DocxWriter
from utils.file_ops import get_supported_files

def main():
    # 1. 加载环境变量 (读取 .env 文件中的 API Key)
    load_dotenv()
    
    # --- 任务配置区 ---
    INPUT_DIR = "./data/inputs"          # 存放待处理文件的文件夹
    OUTPUT_DIR = "./data/outputs"        # 存放处理结果的文件夹
    PROMPT_FILE = "./data/prompt.txt"    # 自定义 Prompt 模板文件
    OUTPUT_FORMAT = ".docx"              # 期望输出的格式 (.txt 或 .docx)
    
    # 确保基础的文件夹存在，方便第一次运行
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 如果没有 Prompt 文件，自动生成一个测试用的模板
    if not os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write("请帮我提取以下文档中的核心观点，并分点总结：\n\n<DOCUMENT>\n{document_content}\n</DOCUMENT>")
        print(f"已自动生成默认 Prompt 模板: {PROMPT_FILE}")

    # 2. 初始化所有核心组件
    print("正在初始化大模型引擎与组件...")
    try:
        engine = LLMEngine() # 默认使用 DeepSeek
    except ValueError as e:
        print(f"初始化失败: {e}")
        return

    loader = PromptLoader(template_path=PROMPT_FILE)
    
    # 3. 扫描输入文件夹
    files_to_process = get_supported_files(INPUT_DIR)
    if not files_to_process:
        print(f"在 {INPUT_DIR} 中没有找到支持的文件 (.txt, .docx)，请放入测试文件后重试。")
        return
        
    print(f"找到 {len(files_to_process)} 个待处理文件，开始批量作业...")
    
    # 4. 执行批量处理循环
    for i, file_path in enumerate(files_to_process, 1):
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        print(f"[{i}/{len(files_to_process)}] 正在处理: {filename} ...")
        
        try:
            # 步骤 A: 读取文档
            if ext == '.txt':
                parser = TxtParser()
            elif ext in ['.doc', '.docx']:
                parser = DocxParser()
            else:
                continue
                
            document_text = parser.extract_text(file_path)
            if not document_text:
                print(f"  -> 警告: {filename} 是空文件，已跳过。")
                continue
                
            # 步骤 B: 组装 Prompt
            final_prompt = loader.build_prompt(document_content=document_text)
            
            # 步骤 C: 请求大模型
            result_text = engine.generate_response(prompt=final_prompt)
            if result_text.startswith("ERROR:"):
                print(f"  -> 处理 {filename} 时模型返回错误，已跳过。")
                continue
                
            # 步骤 D: 保存结果
            # 构造输出文件名: 原文件名_processed.后缀
            base_name = os.path.splitext(filename)[0]
            output_name = f"{base_name}_processed{OUTPUT_FORMAT}"
            output_path = os.path.join(OUTPUT_DIR, output_name)
            
            if OUTPUT_FORMAT == '.txt':
                writer = TxtWriter()
            elif OUTPUT_FORMAT == '.docx':
                writer = DocxWriter()
                
            success = writer.save_result(content=result_text, output_path=output_path)
            if success:
                print(f"  -> 成功! 结果已保存至: {output_path}")
                
        except Exception as e:
            print(f"  -> ❌ 处理 {filename} 时发生严重错误: {str(e)}")

    print("\n🎉 批量任务执行完毕！")

if __name__ == "__main__":
    main()