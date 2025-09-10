from abc import ABC, abstractmethod
from typing import  Any
from llama_index.core import VectorStoreIndex, Document
from ..processors import BaseFileProcessor


class RAGSystem:
    def __init__(self):
        self.file_processors: dict[str, BaseFileProcessor] = {}
        self.knowledge_bases: dict[str, VectorStoreIndex] = {}
        self.thread_sessions: dict[str, Any] = {}
    
    def register_file_processor(self, file_type: str, processor: BaseFileProcessor):
        self.file_processors[file_type] = processor
    
    def upload_knowledge(self, file_path: str, kb_id: str, chunk_strategy: str = "token") -> bool:
        file_ext = file_path.split('.')[-1].lower()
        if file_ext not in self.file_processors:
            return False
            
        documents = self.file_processors[file_ext].process(file_path, chunk_strategy)
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