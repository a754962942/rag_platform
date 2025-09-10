from llama_index.core import Document
from .abc import BaseFileProcessor

class ExcelProcessor(BaseFileProcessor):
    """Excel文件处理器"""
    def process(self, file_path: str, chunk_strategy: str = "token") -> list[Document]:
        pass