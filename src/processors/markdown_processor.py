from curses import meta
from llama_index.core import Document
from .abc import BaseFileProcessor
from llama_index.core.node_parser import MarkdownNodeParser
class MarkdownProcessor(BaseFileProcessor):
    FILE_TYPE = "md"
    """Markdown文件处理器"""
    def __init__(self):
        self.parser = MarkdownNodeParser()
    def process(self, file_path: str,metadata:dict=None, chunk_strategy: str = "markdown") -> list[Document]:
        if not isinstance(metadata,dict):
            metadata = {}
        else:
            metadata = metadata.copy()
        metadata.update({
            "file_path": file_path,
            "file_type": chunk_strategy
        })
        with open(file_path,"rb")as  f:
            file_content =f.read()
        
        document=Document(
            text=file_content,
            metadata=metadata
        )
        nodes = self.parser.get_nodes_from_documents([document])
        return [Document(text=node.get_content(),metadata=node.metadata) for node in nodes ]