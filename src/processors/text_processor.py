from llama_index.core import Document
from .abc import BaseFileProcessor
from llama_index.core.node_parser import (
    TokenTextSplitter,
    SentenceSplitter,
)


class TextProcessor(BaseFileProcessor):
    FILE_TYPES = ["text","txt"]
    """文本文件处理器"""
    def __init__(self):
        self.splitters = {
            "token": TokenTextSplitter(),
            "sentence": SentenceSplitter(),
        }
    
    def process(self, file_path, chunk_strategy = "token",metadata:dict=None) -> list[Document]:
        if not isinstance(metadata, dict):
            metadata = {}
        else:
            metadata = metadata.copy()
        metadata.update({
            "file_path": file_path,
            "file_type": "markdown"
        })
        with open(file_path, 'r') as f:
            text = f.read()
        document = Document(
            text=text,
            metadata=metadata
        )
        splitter = self.splitters.get(chunk_strategy, self.splitters["token"])
        nodes = splitter.get_nodes_from_documents(documents=[document])
        return [Document(text=node.get_content(),metadata=node.metadata) for node in nodes]