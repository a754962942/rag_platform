from uuid import UUID
from ..model.knowledge import  knowledge_base
from typing import Union

KNOWLEDGE_BASE_SINGLETON:list[knowledge_base] = []

def get_knowledge(id:UUID=None)->Union[knowledge_base,list[knowledge_base],None]:
    if id:
        for kb in KNOWLEDGE_BASE_SINGLETON:
            if kb.id == id:
                return kb
        return None
    else:
        return KNOWLEDGE_BASE_SINGLETON

def store_knowledge(kb:knowledge_base)->bool:
    for k in KNOWLEDGE_BASE_SINGLETON:
        if kb.id == k.id:
            return False
    KNOWLEDGE_BASE_SINGLETON.append(kb)
    return True

def update_knowledge(kb:knowledge_base)->bool:
    for i, k in enumerate(KNOWLEDGE_BASE_SINGLETON):
        if kb.id == k.id:
            KNOWLEDGE_BASE_SINGLETON[i] = kb
            return True
    return False

def delete_knowledge(id:UUID)->bool:
    for i, k in enumerate(KNOWLEDGE_BASE_SINGLETON):
        if id == k.id:
            KNOWLEDGE_BASE_SINGLETON.pop(i)
            return True
    return False
