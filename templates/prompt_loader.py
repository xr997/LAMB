import os

class PromptLoader:
    """
    Prompt 模板加载与动态组装引擎。
    负责读取外部的 Prompt 模板文件，并将从文档中提取的文本动态注入到占位符中。
    """

    def __init__(self, template_path: str = None, default_template: str = None):
        """
        初始化模板加载器。
        
        Args:
            template_path (str, optional): 外部 Prompt 模板文件的路径（推荐）。
            default_template (str, optional): 如果没有文件，直接传入的字符串模板。
        """
        self.template = ""
        
        # 优先从文件加载模板
        if template_path:
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"找不到 Prompt 模板文件: {template_path}")
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.template = f.read()
            except Exception as e:
                raise Exception(f"读取模板文件失败: {str(e)}")
        
        # 如果没有文件，则使用传入的默认字符串模板
        elif default_template:
            self.template = default_template
            
        # 如果都没提供，给一个极其基础的默认模板（兜底）
        else:
            self.template = "请阅读并处理以下文档内容：\n\n<DOCUMENT>\n{document_content}\n</DOCUMENT>\n\n请给出你的处理结果："

    def build_prompt(self, **kwargs) -> str:
        """
        动态组装 Prompt。
        使用 Python 内置的字符串 format 机制。
        
        用法示例:
            loader.build_prompt(document_content="你好，世界", user_name="张三")
            这会把模板里所有的 {document_content} 和 {user_name} 替换掉。
            
        Args:
            **kwargs: 需要注入到模板中的键值对参数。
            
        Returns:
            str: 组装完毕，可以直接发给 LLM 的最终 Prompt。
        """
        try:
            # 使用 format 方法将传入的变量填入模板的 {xxx} 占位符中
            return self.template.format(**kwargs)
        except KeyError as e:
            # 如果模板里写了 {A} 但你没传 A，会在这里报错提示
            raise KeyError(f"Prompt 模板中存在未被填充的变量占位符: {str(e)}")
        except IndexError:
            raise ValueError("Prompt 模板格式有误，请确保使用了命名占位符，例如 {document_content} 而不是 {}")
        except Exception as e:
            raise Exception(f"组装 Prompt 时发生未知错误: {str(e)}")