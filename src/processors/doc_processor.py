
from .abc import BaseFileProcessor
from llama_index.core import Document
from llama_index.readers.file import  DocxReader
from pathlib import Path
class DocProcessor(BaseFileProcessor):
    FILE_TYPES = ["docx","doc"]
    def __init__(self):

        self.parser = DocxReader()
    """Word文档处理器"""
    def process(self, file_path: str, chunk_strategy: str = "docx",metadata:dict=None) -> list[Document]:
        if not isinstance(metadata,dict):
            metadata = {}
        else:
            metadata = metadata.copy()
        metadata.update({
            "file_path":file_path,
            "file_type":chunk_strategy
        })
        docs = self.parser.load_data(file=Path(file_path))
        return docs
