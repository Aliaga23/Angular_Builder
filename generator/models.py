# generator/models.py

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Position(BaseModel):
    x: int
    y: int

class Size(BaseModel):
    width: int
    height: int

class Component(BaseModel):
    id: str
    type: str
    name: str
    position: Position
    size: Size
    props: Dict[str, Any]
    zIndex: Optional[int] = None
    parentId: Optional[str] = None
    children: Optional[List[str]] = []

class Page(BaseModel):
    name: str
    components: List[Component]
    isDefault: Optional[bool] = False

class AngularAppSchema(BaseModel):
    appName: str
    backgroundColor: Optional[str] = "#121212"
    defaultPage: str
    pages: List[Page]

