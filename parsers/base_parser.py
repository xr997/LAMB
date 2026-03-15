from abc import ABC, abstractmethod
import os

class BaseParser(ABC):
    """
    所有文件解析器的抽象基类。
    任何新增的文件格式解析器（如 PDF, Markdown）都必须继承此类并实现 extract_text 方法。
    """

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        从指定文件中提取纯文本。
        
        Args:
            file_path (str): 输入文件的绝对或相对路径。
            
        Returns:
            str: 提取出的纯文本内容。
            
        Raises:
            FileNotFoundError: 如果文件不存在。
            Exception: 解析过程中的其他异常。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到文件: {file_path}")
        pass