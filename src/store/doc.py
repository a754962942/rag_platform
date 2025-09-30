from typing import Union

from ..model.doc import  doc
from uuid import UUID
DOC_SINGLETON:dict[UUID,list[doc]]= {}


def store_doc(kb_id:UUID,d:doc)->bool:
    if not DOC_SINGLETON.get(kb_id,None):
        DOC_SINGLETON[kb_id] = []
    for dc in DOC_SINGLETON[kb_id]:
        if dc.id == doc.id:
            return True
    DOC_SINGLETON[kb_id].append(d)
    return True

def delete_doc(kb_id:UUID,doc_id:UUID)->bool:
    if not kb_id or not doc_id:
        return False
    if not DOC_SINGLETON.get(kb_id,None):
        return True
    for i,dc in enumerate(DOC_SINGLETON[kb_id]):
        if dc.id == doc_id:
            DOC_SINGLETON[kb_id].pop(i)
            return True
    return False

def update_doc(kb_id:UUID,d:doc)->bool:
    if not kb_id or not d:
        return False
    if not DOC_SINGLETON.get(kb_id,None):
        return False
    for i,dc in enumerate(DOC_SINGLETON[kb_id]):
        if dc.id == d.id:
            DOC_SINGLETON[kb_id][i] = d
            return True
    return False

def get_docs_by_kb_id(kb_id:UUID )->Union[list[doc],None]:
    if not DOC_SINGLETON.get(kb_id,None):
        return None
    return DOC_SINGLETON[kb_id]
def get_doc_by_doc_id(kb_id:UUID,doc_id:UUID)->Union[doc,None]:
    if not DOC_SINGLETON.get(kb_id,None):
        return None
    for doc in DOC_SINGLETON[kb_id]:
        if doc.id == doc_id:
            return doc
    return None

