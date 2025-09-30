from  dataclasses import  dataclass
from uuid import UUID
from pydantic import  BaseModel
@dataclass
class knowledge_base(BaseModel):
    id:UUID
    name:str
    desc:str

