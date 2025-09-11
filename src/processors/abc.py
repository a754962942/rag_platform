from abc import ABC, abstractmethod, ABCMeta
from typing import Any

from llama_index.core import Document

class ProcessorMeta(ABCMeta):
    _registry = {}
    def __init__(cls, name, bases, attrs):
        if name !="BaseFileProcessor":
            file_types = getattr(cls,"FILE_TYPES",[getattr(cls,"FILE_TYPE",None)])
            file_type = getattr(cls,"FILE_TYPE",None)
            if  not file_types and file_type:
                file_types = [file_type]
            print(f"{cls}:{file_types}")
            if isinstance(file_types,list):
                for ft in file_types:
                    if ft:
                        cls._registry[ft] = cls
            else:
                cls._registry[file_types] = cls
        super().__init__(name,bases,attrs)

class BaseFileProcessor(ABC,metaclass=ProcessorMeta):
    FILE_TYPES = None
    FILE_TYPE = None
    """文件处理基类接口"""
    @abstractmethod
    def process(self, file_path: str,**kwargs) -> list[Document]:
        """处理文件并返回Document列表"""
        pass
    @classmethod
    def get_processor(cls,file_type):
        return cls._registry.get(file_type,None)
    @classmethod
    def get_all_processor(cls,)->dict[str,Any]:
        return cls._registry
