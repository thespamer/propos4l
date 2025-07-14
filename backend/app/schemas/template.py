from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional


class TemplateSectionBase(BaseModel):
    name: str
    content: str
    order: int
    metadata: Dict = {}


class TemplateSectionCreate(TemplateSectionBase):
    pass


class TemplateSectionResponse(TemplateSectionBase):
    id: int


class TemplateBase(BaseModel):
    name: str
    description: str = ""
    structure: Dict = {}


class TemplateCreate(TemplateBase):
    pass


class TemplateResponse(TemplateBase):
    id: int
    creation_date: datetime
    sections: List[TemplateSectionResponse]
    
    class Config:
        orm_mode = True
