import os

from core.rag_system import RAGSystem
from dotenv import  load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding,DashScopeTextEmbeddingModels


load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
# TODO 后续支持模型选择
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
    rag.install_processor()
    return rag

if __name__ == "__main__":

    rag = init_rag_system()
    # # 示例用法
    rag.upload_knowledge("data/sample.txt", "kb1")
    rag.upload_knowledge("data/量子计算.txt", "kb2")
    rag.upload_knowledge("./README.md","kb3")
    response = rag.query(["kb1"], "thread1", "系统使用什么策略来进行隔离?")
    print(response)
    response2 = rag.query(["kb2"],thread_id="thread2", query="量子计算的挑战有哪些?")
    print(response2)
    response3 = rag.query(["kb3"],"thread3",query="稀疏搜索使用的技术栈是什么?")
    print(response3)
    response4 = rag.query(["kb3"],"thread3",query="稠密呢?")
    print(response4)