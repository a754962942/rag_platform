import os

from fastapi import FastAPI,UploadFile

from ..core.rag_system import RAGSystem
from ..model import doc,knowledge_base
from uuid import uuid4,UUID
from ..processors import BaseFileProcessor
from ..store import *

app = FastAPI()
rag_sys = RAGSystem()
rag_sys.install_processor()

@app.post("/knowledge-bases")
def create_knowledge(kb_name:str,kb_desc:str = ""):
    kb = knowledge_base(name=kb_name,desc=kb_desc,id=uuid4())
    is_success = store_knowledge(kb)
    if is_success:
        return {"code": 0, "data": kb.model_dump_json(), "msg": "success"}
    else:
        return {"code":-1,"msg":"store knowledge base failed."}
@app.get("/knowledge-bases")
def query_knowledge(page:int,pageSize:int):
    knowledge_list = get_knowledge()
    start_index = max(0, min((page*pageSize), len(knowledge_list)))
    end_index = max(0, min((pageSize*(page+1)), len(knowledge_list)))
    if start_index> end_index:
        print(f"start_index>end_index:{start_index}>{end_index}")
        return {"code":0,"data":[],"msg":"success"}
    result = knowledge_list[start_index:end_index]
    return {"code":0,"data":result,"msg":"success"}
@app.get("/knowledge-bases/{kb_id}")
def get_knowledge_base_detail(kb_id:str):
    result = get_knowledge(UUID(kb_id))
    return {"code":0,"data":result,"msg":"success"}
@app.post("/knowledge-bases/retrieval-config")
def update_knowledge_base(kb_id:str,kb_name:str,kb_desc:str):
    kb = knowledge_base(id=UUID(kb_id),name=kb_name,desc=kb_desc)
    is_success = update_knowledge(kb)
    if is_success:
        return {"code":0,"msg":"success"}
    else:
        return {"code":-1,"msg":"update knowledge failed."}
@app.delete("/knowledge-bases/{kb_id}")
def delete_knowledge_bases(kb_id:str):
    is_success = delete_knowledge(UUID(kb_id))
    if is_success:
        return {"code":0,"msg":"success"}
    else:
        return {"code":-1,"msg":"delete knowledge failed."}
@app.post("/knowledge-bases/documents")
def upload_knowledge_bases(file: UploadFile,kb_id:str):
    try:
        dir_path = os.path.join("qanything_llamaindex/data",kb_id)
        os.makedirs(dir_path,0o777,True)
        file_content = file.file.read()
        filename = file.filename
        with open(f"{dir_path}/{filename}","wb") as f:
            f.write(file_content)
        d = doc(id=uuid4(),doc_name=file.filename)
        k_id = UUID(kb_id)
        is_success = store_doc(k_id,d)
        if is_success:
            return {"code":0,"msg":"success"}
        else:
            return {"code":-2,"msg":"upload file failed."}
    except Exception as e:
        print(e)
        return {"code":-1,"msg":"upload file failed."}

@app.get("/knowledge-bases/documents")
def get_documents(page:int,pageSize:int,kb_id:str):
    k_id=UUID(kb_id)
    docs = get_docs_by_kb_id(kb_id=k_id)
    start_index = max(0, min((page * pageSize), len(docs)))
    end_index = max(0, min((pageSize * (page + 1)), len(docs)))
    if start_index > end_index:
        print(f"start_index>end_index:{start_index}>{end_index}")
        return {"code": 0, "data": [], "msg": "success"}
    result = docs[start_index:end_index]
    return {"code":0,"data":result,"msg":"success"}
@app.get("/documents/chunks")
def get_chunks(doc_id:str,kb_id:str):
    k_id= UUID(kb_id)
    d_id = UUID(doc_id)
    doc = get_doc_by_doc_id(kb_id=k_id,doc_id=d_id)
    if doc:
        file_ext = doc.doc_name.split(".")[-1].lower()
        file_path = os.path.join("qanything_llamaindex/data",kb_id,doc.doc_name)
        processor_mapper = BaseFileProcessor.get_all_processor()
        processor = processor_mapper.get(file_ext,None)
        if processor and isinstance(processor,BaseFileProcessor):
            documents = processor.process(file_path=file_path)
            return {"code":0,"data":documents,"msg":"success"}
        else:
            return {"code":-1,"msg":f"up to now,{file_ext} type not allowed."}
    else:
        return {"code":-1,"msg":f"can not find doc by doc_id {doc_id}"}
@app.delete("/documents")
def delete_docs(doc_id:list[str],kb_id:str):
    k_id = UUID(kb_id)
    d_ids = [UUID(d) for d in doc_id]
    fail_msg:str = ""
    for d_id in d_ids:
        is_success = delete_doc(kb_id=k_id,doc_id=d_id)
        if not is_success:
            fail_msg.join(f"doc_id {d_id.__str__()} delete failed.\n")
    if len(fail_msg)<1:
        return {"code":0,"msg":"success"}
    else:
        return {"code":-1,"msg":fail_msg}

@app.post("/knowledge-bases/search")
def search_by_kb_id(question:str,kb_id:list[str]):
    from ..model.doc import doc
    docs:list[doc] = []
    doc_kb_id_map:dict[str,str] = {}
    for k_id in kb_id:
        id = UUID(k_id)
        kb =  get_knowledge(id=id)
        docs_by_kb_id = get_docs_by_kb_id(kb_id=kb.id)
        for d in docs_by_kb_id:
            if d:
                doc_kb_id_map[d.id.__str__()]=k_id
                docs.append(d)
    files_path:list[str]=[]
    for doc in docs:
        k_id = doc_kb_id_map.get(doc.id.__str__(),"")
        if len(k_id)<1:
            return {"code":-1,"msg":"kb_id is invalid"}
        else:
            file_path = os.path.join("qanything_llamaindex/data",k_id,doc.doc_name)
            files_path.append(file_path)
    result = rag_sys.query_test(question=question,files_path=files_path)
    return result
@app.post("/knowledge-bases/ask")
def ask_by_kb_id(question:str,kb_id:list[str]):
    docs_path :list[str] = []
    docs_path_kb_id_map :dict[str,str]={}

    kb_ids = [UUID(k_id) for k_id in kb_id]
    for k_id in kb_ids:
        docs = get_docs_by_kb_id(kb_id=k_id)
        if docs :
            docs_path.extend([
                os.path.join("qanything_llamaindex/data",k_id.__str__(),d.doc_name)
                for d in docs
            ])
            docs_path_kb_id_map.update({
                os.path.join("qanything_llamaindex/data",k_id.__str__(),d.doc_name):k_id.__str__()
                for d in docs
            })
    fail_msg = ""
    for fp in docs_path:
        is_success = rag_sys.upload_knowledge(file_path=fp,kb_id=docs_path_kb_id_map.get(fp,""))
        if not is_success:
            fail_msg.join(f"{fp} to vector failed. kb_id is {docs_path_kb_id_map.get(fp)}")
    if len(fail_msg)>1:
        return {"code":-1,"msg":fail_msg}
    else:
        response = rag_sys.query(query=question)



@app.get("/query/sessions")
def get_query_sessions(session_id:str):
    pass
@app.post("/config/llm")
def change_llm(llm:str):
    pass
@app.get("/system/metrics")
def get_metrics():
    pass
@app.get("/system/health")
def health():
    pass
@app.post("/knowledge-bases/reindex")
def reindex_knowledge(kb_id:str):
    pass
@app.post("/documents/reprocess")
def reprocess_documents(doc_id:str):
    pass