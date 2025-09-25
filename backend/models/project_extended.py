from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    initial_prompt: Optional[str] = None
    template_id: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class ProjectVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str
    code: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCollaborator(BaseModel):
    user_id: str
    role: str  # "owner", "editor", "viewer"
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    initial_prompt: Optional[str] = None
    owner_id: str
    template_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    is_featured: bool = False
    generated_code: Optional[str] = None
    current_version: str = "1.0.0"
    versions: List[ProjectVersion] = []
    collaborators: List[ProjectCollaborator] = []
    tech_stack: List[str] = ["React", "TypeScript", "Tailwind CSS"]
    deployment_url: Optional[str] = None
    preview_image: Optional[str] = None
    likes_count: int = 0
    views_count: int = 0
    forks_count: int = 0
    tags: List[str] = []

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_name: str
    owner_avatar: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_public: bool
    is_featured: bool
    current_version: str
    tech_stack: List[str]
    deployment_url: Optional[str]
    preview_image: Optional[str]
    likes_count: int
    views_count: int
    forks_count: int
    tags: List[str]

class DeploymentRequest(BaseModel):
    project_id: str
    subdomain: Optional[str] = None