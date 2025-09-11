from abc import ABC, abstractmethod
from typing import  Any
from llama_index.core import VectorStoreIndex, Document
from processors import BaseFileProcessor
from processors import (
            TextProcessor,
            MarkdownProcessor,
            CsvProcessor,
            ExcelProcessor,
            DocProcessor,
            ProcessorMeta
        )

class RAGSystem:
    def __init__(self):
        self.knowledge_bases: dict[str, VectorStoreIndex] = {}
        self.thread_sessions: dict[str, Any] = {}
        self.processorMap:dict[Any,BaseFileProcessor] = {}
        self.supportProcessorMap:dict[str,Any] = {}
    def install_processor(self):
        """所有支持的processor全部在此示例化，统一注册"""
        processors = [cls() for cls in BaseFileProcessor.__subclasses__()]
        
        self.processorMap.update({type(p):p for p in processors})
        self.supportProcessorMap.update(BaseFileProcessor.get_all_processor())
        
        print(f"已注册的processor：{self.processorMap}")
        print(f"支持的processor：{self.supportProcessorMap}")

    def upload_knowledge(self, file_path: str, kb_id: str, chunk_strategy: str = "token") -> bool:
        file_ext = file_path.split('.')[-1].lower()
        if file_ext not in self.supportProcessorMap:
            return False
        process_type = self.supportProcessorMap[file_ext]
        process = self.processorMap[process_type]
        documents = process.process(file_path, chunk_strategy=chunk_strategy)
        self.knowledge_bases[kb_id] = VectorStoreIndex.from_documents(documents)
        return True
    
    def query(self, kb_ids: list[str], thread_id: str, query: str) -> str:
    
        if thread_id not in self.thread_sessions:
            self.thread_sessions[thread_id] = {
                'kb_ids': kb_ids,
                'history': []
            }
        
        indexes = [self.knowledge_bases[kb_id] for kb_id in kb_ids 
                  if kb_id in self.knowledge_bases]
        
        if not indexes:
            return "未找到指定的知识库"
            
        query_engine = indexes[0].as_query_engine()
        response = query_engine.query(query)
        self.thread_sessions[thread_id]['history'].append((query, str(response)))
        return str(response)