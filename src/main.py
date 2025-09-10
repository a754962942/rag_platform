import os

from core.rag_system import RAGSystem
from processors import (
    TextProcessor,
)
from dotenv import  load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding,DashScopeTextEmbeddingModels

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
Settings.llm = OpenAILike(
    model="qwen-plus",
api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=api_key,
    is_chat_model=True
)
local_embedding = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
    embed_batch_size=6,
    embed_input_length=8192
)
Settings.embed_model = local_embedding
def init_rag_system() -> RAGSystem:
    """初始化RAG系统"""
    rag = RAGSystem()
    # 注册文件处理器
    rag.register_file_processor("txt", TextProcessor())
    rag.register_file_processor("text", TextProcessor())
    return rag

if __name__ == "__main__":
    rag = init_rag_system()
    # 示例用法
    rag.upload_knowledge("data/sample.txt", "kb1")
    rag.upload_knowledge("data/量子计算.txt", "kb2")
    response = rag.query(["kb1"], "thread1", "系统使用什么策略来进行隔离?")
    response2 = rag.query(["kb2"],thread_id="thread2", query="量子计算的挑战有哪些?")
    print(response)
    print(response2)