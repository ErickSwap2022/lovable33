from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    initial_prompt: Optional[str] = None

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    initial_prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    generated_code: Optional[str] = None

class ChatMessage(BaseModel):
    type: str  # "user" or "assistant"
    content: str

class GenerateCodeRequest(BaseModel):
    prompt: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))