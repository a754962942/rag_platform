from llama_index.core import Document
from .abc import BaseFileProcessor
from llama_index.readers.file import PandasCSVReader,PandasExcelReader
from pathlib import Path


class ExcelProcessor(BaseFileProcessor):
    FILE_TYPES = ["xlsx","xls"]
    """Excel文件处理器"""
    def __init__(self):
        self.parser = PandasExcelReader()
    def process(self, file_path: str, metadata:dict=None,chunk_strategy:str = "excel") -> list[Document]:
        if not isinstance(metadata,dict):
            metadata = dict
        else:
            metadata = metadata.copy()
        metadata.update({
            "file_path":file_path,
            "file_type":chunk_strategy
        })
        docs = self.parser.load_data(file=Path(file_path))
        return docs
class CsvProcessor(BaseFileProcessor):
    FILE_TYPE = "csv"
    """CSV 文件处理器"""
    def __init__(self):
        self.parser =PandasCSVReader()
    def process(self, file_path: str,metadata:dict=None,chunk_strategy:str="csv") -> list[Document]:
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
