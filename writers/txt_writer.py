from .base_writer import BaseWriter

class TxtWriter(BaseWriter):
    """
    将大模型的输出结果保存为 .txt 文件的生成器。
    """

    def save_result(self, content: str, output_path: str) -> bool:
        # 确保输出目录存在
        self._ensure_dir(output_path)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存 TXT 文件 {output_path} 时发生错误: {str(e)}")
            return False