from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class TemplateCreate(BaseModel):
    name: str
    description: str
    category: str
    code: str
    preview_image: Optional[str] = None
    tags: List[str] = []

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    code: str
    preview_image: Optional[str] = None
    tags: List[str] = []
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_featured: bool = False
    is_public: bool = True
    usage_count: int = 0
    likes_count: int = 0

class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    preview_image: Optional[str]
    tags: List[str]
    author_name: str
    created_at: datetime
    is_featured: bool
    usage_count: int
    likes_count: int