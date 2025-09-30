from llama_index.core import StorageContext,Document,VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever,QueryFusionRetriever
from llama_index.core.schema import  NodeWithScore
from  llama_index.vector_stores.elasticsearch import ElasticsearchStore,AsyncBM25Strategy
from  dotenv import load_dotenv
import  os

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
elastic_config ={"index_name":"my_index","es_url":"http://127.0.0.1:9200"}
class hybrid_retriever:
    class HybridNodeWithScore:
        source_type:str="Vector" or "ElasticSearch"
        def __init__(self,node:NodeWithScore,source_type:str):
            self.source_type = source_type
            self.node = node
        def get_source_type(self):
            return self.source_type
        def get_node(self)->NodeWithScore:
            return self.node
        @property
        def id_(self):
            return self.node.id_
        @property
        def node_id(self):
            return self.node.node_id
        @property
        def text(self):
            return self.node.text
        @property
        def content(self):
            return self.node.get_content()
        @property
        def score(self):
            return self.node.score
        @score.setter
        def score(self,score:float):
            self.node.score = score
    def __init__(self,vector_documents:list[Document]=None,fts_documents:list[Document]=None,top_k:int=3,weights:list[float]=[0.5,0.5]):
        """
        :param documents: 切分好的documents
        :param top_k: top_k
        :param weights: [向量权重,关键词权重]
        """
        self.retrievers:list = []
        if vector_documents:
            self.vector_store = VectorStoreIndex.from_documents(documents=vector_documents)
            self.top_k = top_k
            self.weight_dict = {"Vector":weights[0],"ElasticSearch":weights[1]}
            self.vector_retriever = VectorIndexRetriever(index=self.vector_store,similarity_top_k=top_k)
            self.retrievers.append(self.vector_retriever)
        # 如需使用BM25进行关键词索引，则中文分词器需要额外对tokenizer进行重新封装，否则所有上下分score均为0，即关键词索引失效
        # 此处使用elasticSearch进行关键词检索
        if fts_documents:
            self.elasticsearch_store = ElasticsearchStore(
                index_name=elastic_config["index_name"],
                es_url=elastic_config["es_url"],
                retrieval_strategy=AsyncBM25Strategy())
            self.elasticsearch_context = StorageContext.from_defaults(vector_store=self.elasticsearch_store)
            self.elasticsearch_retriever = VectorStoreIndex(nodes=fts_documents,storage_context=self.elasticsearch_context).as_retriever()
            self.retrievers.append(self.elasticsearch_retriever)
        if not self.retrievers or len(self.retrievers)<1:
            raise ValueError("请至少选择一种检索方式")
        self.hybrid_retriever = QueryFusionRetriever(retrievers=self.retrievers,retriever_weights=weights,similarity_top_k=top_k)
    def __enter__(self):
        self._is_open = True
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_open:
            self.close()
        return False
    def close(self):
        self.elasticsearch_store.close()
    def retriever(self,question:str)->list[HybridNodeWithScore]:
        # result = self.hybrid_retriever.retrieve(question)
        result1 = self.vector_retriever.retrieve(question)
        result2 = self.elasticsearch_retriever.retrieve(question)
        result_list:list[hybrid_retriever.HybridNodeWithScore] = []
        for r in result1:
            rr = self.HybridNodeWithScore(r,"Vector")
            result_list.append(rr)
        for r in result2:
            rr = self.HybridNodeWithScore(r,"ElasticSearch")
            result_list.append(rr)
        result_map:dict[int,hybrid_retriever.HybridNodeWithScore] = {}
        for res in result_list:
            if res:
                hs = result_map.get(hash(res.content), None)
                if hs:
                    modify_score = res.score * self.weight_dict.get(res.get_source_type())
                    if modify_score > hs.score:
                        modify_res = res
                        modify_res.score = modify_score
                        result_map.update({hash(modify_res.content): modify_res})
                else:
                    modify_res = res
                    modify_res.score = res.score*self.weight_dict.get(res.get_source_type())
                    result_map.update({hash(modify_res.content):modify_res})

        result_list = sorted(result_map.values(), key=lambda x: x.score or 0.0, reverse=True)
        if len(result_list)>self.top_k:
            result_list = result_list[:self.top_k]
        else:
            pass
        return result_list

from llama_index.core import Document
from llama_index.core.text_splitter import TokenTextSplitter
class TextProcessor():
    FILE_TYPES = ["text", "txt"]
    """文本文件处理器"""

    def __init__(self):
        self.splitters = {
            "token": TokenTextSplitter(),
        }

    def process(self, file_path, chunk_strategy="token", metadata: dict = None) -> list[Document]:
        if not isinstance(metadata, dict):
            metadata = {}
        else:
            metadata = metadata.copy()
        metadata.update({
            "file_path": file_path,
            "file_type": "markdown"
        })
        with open(file_path, 'r') as f:
            text = f.read()
        document = Document(
            text=text,
            metadata=metadata
        )
        splitter = self.splitters.get(chunk_strategy, self.splitters["token"])
        nodes = splitter.get_nodes_from_documents(documents=[document])
        return [Document(text=node.get_content(), metadata=node.metadata) for node in nodes]


if __name__ == '__main__':
    try:
        file_path = "/Users/duhongwei/workspace/qanything_llamaindex/src/core/example2.txt"
        processor = TextProcessor()
        documents = processor.process(file_path=file_path)
        with hybrid_retriever(documents=documents,top_k=5,weights=[0.3,0.7]) as hybrid:
            question = "量子计算和经典计算的区别是什么？"
            result = hybrid.retriever(question)
            for res in result:
                # pass
                print(f"score:{res.score}\ntext:{res.content}")
    except Exception as e:
        print(e)









