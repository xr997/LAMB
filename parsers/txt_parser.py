from .base_parser import BaseParser

class TxtParser(BaseParser):
    """
    专门用于处理 .txt 纯文本文件的解析器。
    """

    def extract_text(self, file_path: str) -> str:
        # 调用父类方法，确保文件存在
        super().extract_text(file_path)
        
        try:
            # 使用 utf-8 编码读取，并处理可能的 BOM 头
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            return content.strip()
        except UnicodeDecodeError:
            # 如果 utf-8 失败，尝试系统默认的 gbk 编码（常见于 Windows 中文环境）
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
            return content.strip()
        except Exception as e:
            raise Exception(f"读取 TXT 文件 {file_path} 时发生错误: {str(e)}")