from typing import  Any
from llama_index.core import VectorStoreIndex, Document,SummaryIndex
from llama_index.core.llms import ChatMessage
from processors import BaseFileProcessor
from processors import (
            TextProcessor,
            MarkdownProcessor,
            CsvProcessor,
            ExcelProcessor,
            DocProcessor,
            ProcessorMeta
        )

from llama_index.core import Settings
from llama_index.core.llms import LLM

from .retriever import hybrid_retriever


class RAGSystem:
    def __init__(self,is_vector_index:bool=False,is_full_search:bool=False,is_hybrid:bool=True,similarity_top_k:int = 3,llm:LLM =None):
        if is_hybrid:
            self.is_vector_index = True
            self.is_full_search = True
        elif is_vector_index:
            self.is_vector_index = True
        elif is_full_search:
            self.is_full_search = True
        if llm :
            self.llm  = llm
        else:
            self.llm = Settings.llm
        self.similarity_top_k = similarity_top_k
        self.vector_knowledge_bases: dict[str, list[Document]] = {}
        self.fts_knowledge_bases:dict[str,list[Document]] = {}
        self.thread_sessions: dict[str, dict[str,list[str]|list[ChatMessage]]] = {}
        self.processorMap:dict[Any,BaseFileProcessor] = {}
        self.supportProcessorMap:dict[str,Any] = {}

    def install_processor(self):
        """所有支持的processor全部在此示例化，统一注册"""
        processors = [cls() for cls in BaseFileProcessor.__subclasses__()]
        
        self.processorMap.update({type(p):p for p in processors})
        self.supportProcessorMap.update(BaseFileProcessor.get_all_processor())
        
        print(f"已注册的processor：{self.processorMap}")
        print(f"支持的processor：{self.supportProcessorMap}")
    def file_to_documents(self,file_path:str,is_fts:bool=False)->list[Document]:
        file_ext = file_path.split('.')[-1].lower()
        if file_ext not in self.supportProcessorMap:
            return False
        process_type = self.supportProcessorMap[file_ext]
        process = self.processorMap[process_type]
        if is_fts:
            process = self.processorMap[self.supportProcessorMap["text"]]
            documents = process.process(file_path=file_path,chunk_strategy="sentence")
        else:
            documents = process.process(file_path=file_path)
        return documents
    def upload_knowledge(self, file_path: str, kb_id: str,) -> bool:
        if len(kb_id)<1:
            return False
        if self.is_vector_index:
            documents = self.file_to_documents(file_path=file_path)
            if kb_id not in self.vector_knowledge_bases:
                self.vector_knowledge_bases[kb_id] = []
            self.vector_knowledge_bases[kb_id].extend(documents)
        if self.is_full_search:
            documents = self.file_to_documents(file_path=file_path,is_fts=True)
            if kb_id not in self.fts_knowledge_bases:
                self.fts_knowledge_bases[kb_id] = []
            self.fts_knowledge_bases[kb_id].extend(documents)
        return True
    def llm_explain(self,kb_results:list[hybrid_retriever.HybridNodeWithScore],question:str,thread_id:str)->str:
        """
        使用llm能力参照语意/关键词搜索结果做出完整的响应
        :param kb_results: 稠密/稀疏 搜索结果（重排序后）
        :param question: 用户原始问题
        :return: llm一句搜索结果和用户问题合并做出的回答
        """
        history = self.thread_sessions[thread_id]['history']
        context = "\n".join([f"文本信息：{kb.content}\n相关度：{kb.score}" for kb in kb_results])
        from .prompt import  prompt_template
        prompt =  prompt_template.format(context=context,question=question)
        history.append(ChatMessage(role="user",content=prompt))
        response = self.llm.chat(history)
        history.append(ChatMessage(role="assistant",content=response.message.content))
        self.thread_sessions[thread_id]['history'] =  history
        return response.message.content
    def query(self, kb_ids: list[str], thread_id: str, query: str,is_need_llm_explain:bool=True) -> dict[str,Any]|str:
        if thread_id not in self.thread_sessions:
            self.thread_sessions[thread_id] = {
                'kb_ids': kb_ids,
                'history': []
            }
        total_vector_documents = [self.vector_knowledge_bases[kb_id] for kb_id in kb_ids
                         if kb_id in self.vector_knowledge_bases] or None
        vector_documents=[i for documents in total_vector_documents for i in documents] or None
        total_fts_documents = [self.fts_knowledge_bases[kb_id] for kb_id in kb_ids
                                  if kb_id in self.fts_knowledge_bases]  or None
        fts_documents = [i for documents in total_fts_documents for i in documents] or None

        if not vector_documents and not fts_documents:
            return "未找到指定的知识库"
        results =[]
        from .retriever import hybrid_retriever
        with hybrid_retriever(vector_documents=vector_documents,fts_documents=fts_documents, top_k=self.similarity_top_k) as retriever:
            res = retriever.retriever(query)
            results.extend(res)
        if is_need_llm_explain:
            return self.llm_explain(results,query,thread_id)
        return {
            "retriever_result":results
        }
    def query_test(self,question:str,files_path:list[str]):
        total_docs:list[Document]=[]
        for file_path in files_path:
            dcs = self.file_to_documents(file_path=file_path)
            total_docs.extend(dcs)
        index = VectorStoreIndex.from_documents(total_docs)
        query_engine = index.as_query_engine()
        res = query_engine.query(question)
        return res