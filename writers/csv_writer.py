import csv
import os
from typing import List, Dict
from .base_writer import BaseWriter

class CsvWriter(BaseWriter):
    """
    将大模型的批量处理结果聚合保存为单个 CSV 表格的生成器。
    非常适合“作业批改”、“简历筛选”等 N-to-1 的聚合任务。
    """

    def save_result(self, content: List[Dict[str, str]], output_path: str) -> bool:
        """
        注意：这里的 content 接收的是一个字典列表。
        例如: [{"文件名": "张三.docx", "分数": "95", "评语": "很好"}, ...]
        """
        self._ensure_dir(output_path)
        
        if not content:
            print("警告: 没有可写入的数据。")
            return False

        try:
            # 自动提取字典的键作为 CSV 的表头
            headers = content[0].keys()
            
            # 使用 utf-8-sig 编码，防止 Excel 打开中文乱码
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(content)
            return True
        except Exception as e:
            print(f"保存 CSV 文件 {output_path} 时发生错误: {str(e)}")
            return False