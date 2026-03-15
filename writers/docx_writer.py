from .base_writer import BaseWriter

try:
    import docx
except ImportError:
    raise ImportError("缺少依赖库。请在终端运行: pip install python-docx")

class DocxWriter(BaseWriter):
    """
    将大模型的输出结果保存为 .docx 文件的生成器。
    """

    def save_result(self, content: str, output_path: str) -> bool:
        # 确保输出目录存在
        self._ensure_dir(output_path)
        
        try:
            # 创建一个新的 Word 文档
            doc = docx.Document()
            
            # 将大模型输出的内容按换行符分割，逐段写入
            # 这样能保留 LLM 输出的基础分段格式
            paragraphs = content.split('\n')
            for para in paragraphs:
                doc.add_paragraph(para)
                
            # 保存到指定路径
            doc.save(output_path)
            return True
            
        except Exception as e:
            print(f"保存 DOCX 文件 {output_path} 时发生错误: {str(e)}")
            return False