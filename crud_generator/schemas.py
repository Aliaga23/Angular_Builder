from pydantic import BaseModel
from typing import List, Optional

class Attribute(BaseModel):
    name: str
    type: str
    isRequired: Optional[bool] = True

class GenerateRequest(BaseModel):
    name: str  
    attributes: List[Attribute]
    primary_key: Attribute
    auto_increment: bool = True
