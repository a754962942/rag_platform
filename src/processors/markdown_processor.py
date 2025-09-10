from llama_index.core import Document
from .abc import BaseFileProcessor

class MarkdownProcessor(BaseFileProcessor):
    """Markdown文件处理器"""
    def process(self, file_path: str, chunk_strategy: str = "markdown") -> list[Document]:
        pass