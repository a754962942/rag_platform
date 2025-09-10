from llama_index.core import Document
from .abc import BaseFileProcessor
from llama_index.core.node_parser import (
    TokenTextSplitter,
    SentenceSplitter,
)


class TextProcessor(BaseFileProcessor):
    """文本文件处理器"""
    def __init__(self):
        self.splitters = {
            "token": TokenTextSplitter(),
            "sentence": SentenceSplitter(),
        }
    
    def process(self, file_path, chunk_strategy = "token") -> list[Document]:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        splitter = self.splitters.get(chunk_strategy, self.splitters["token"])
        nodes = splitter.get_nodes_from_documents([Document(text=text)])
        return [Document(text=node.text) for node in nodes]