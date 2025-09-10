from abc import ABC, abstractmethod
from llama_index.core import Document
class BaseFileProcessor(ABC):
    """文件处理基类接口"""
    @abstractmethod
    def process(self, file_path: str) -> list[Document]:
        """处理文件并返回Document列表"""
        pass