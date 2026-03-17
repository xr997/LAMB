from .base_parser import BaseParser

try:
    import fitz  # PyMuPDF 的导入名称
except ImportError:
    raise ImportError("缺少依赖库。请在终端运行: pip install pymupdf")

class PdfParser(BaseParser):
    """
    专门用于处理 .pdf 格式文档的解析器。
    """

    def extract_text(self, file_path: str) -> str:
        # 调用父类方法，确保文件存在
        super().extract_text(file_path)
        
        try:
            text_content = []
            # 使用 fitz 打开 PDF 文档
            with fitz.open(file_path) as pdf_doc:
                # 遍历每一页提取纯文本
                for page_num in range(len(pdf_doc)):
                    page = pdf_doc.load_page(page_num)
                    page_text = page.get_text().strip()
                    if page_text:
                        text_content.append(page_text)
                        
            # 将所有页的文本用双换行符拼接起来
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise Exception(f"读取 PDF 文件 {file_path} 时发生致命错误: {str(e)}")