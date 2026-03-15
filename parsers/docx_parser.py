from .base_parser import BaseParser

try:
    import docx
except ImportError:
    raise ImportError("缺少依赖库。请在终端运行: pip install python-docx")

class DocxParser(BaseParser):
    """
    专门用于处理 .docx 格式 Word 文档的解析器。
    """

    def extract_text(self, file_path: str) -> str:
        # 调用父类方法，确保文件存在
        super().extract_text(file_path)
        
        try:
            doc = docx.Document(file_path)
            full_text = []
            
            # 1. 提取所有段落文本
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:  # 过滤掉纯空白段落
                    full_text.append(text)
                    
            # 2. 提取所有表格文本 (用 "|" 简单分隔列，保留基础结构)
            for table in doc.tables:
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            row_data.append(cell_text)
                    if row_data:
                        full_text.append(" | ".join(row_data))
                        
            # 将提取到的所有文本按行拼接
            return "\n".join(full_text)
            
        except Exception as e:
            raise Exception(f"读取 DOCX 文件 {file_path} 时发生错误: {str(e)}")