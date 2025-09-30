from  dataclasses import  dataclass
from uuid import UUID
from pydantic import  BaseModel


@dataclass
class doc(BaseModel):
    id:UUID
    doc_name:str