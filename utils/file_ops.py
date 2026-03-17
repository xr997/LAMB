import os
from typing import List

def get_supported_files(directory: str, supported_extensions: tuple = ('.txt', '.doc', '.docx','.pdf')) -> List[str]:
    """
    遍历指定目录，获取所有支持处理的文件路径。
    
    Args:
        directory (str): 需要遍历的文件夹路径。
        supported_extensions (tuple): 支持的文件后缀元组。
        
    Returns:
        List[str]: 符合条件的文件绝对路径列表。
    """
    if not os.path.exists(directory):
        print(f"警告: 输入目录 {directory} 不存在。")
        return []

    valid_files = []
    # 使用 os.walk 支持多层级文件夹的递归遍历
    for root, _, files in os.walk(directory):
        for file in files:
            # 忽略隐藏文件 (如 macOS 的 .DS_Store)
            if file.startswith('.'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                valid_files.append(os.path.join(root, file))
                
    return valid_files