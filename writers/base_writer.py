from abc import ABC, abstractmethod
import os

class BaseWriter(ABC):
    """
    所有结果生成器的抽象基类。
    """

    def _ensure_dir(self, file_path: str):
        """内部辅助方法：确保输出文件所在的目录存在。"""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    @abstractmethod
    def save_result(self, content: str, output_path: str) -> bool:
        """
        将大模型处理后的内容保存为指定格式的文件。
        
        Args:
            content (str): 大模型返回的文本内容。
            output_path (str): 期望保存的文件路径。
            
        Returns:
            bool: 保存是否成功。
        """
        self._ensure_dir(output_path)
        pass