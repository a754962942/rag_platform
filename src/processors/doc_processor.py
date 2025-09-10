
from .abc import BaseFileProcessor
from llama_index.core import Document

class DocProcessor(BaseFileProcessor):
    """Word文档处理器"""
    def process(self, file_path: str, chunk_strategy: str = "paragraph") -> list[Document]:
        pass