from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class AgentRequest(BaseModel):
    prompt: str
    session_id: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    success: bool
    code: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    optimizations: Optional[str] = None
    confidence_score: Optional[float] = None
    message: str
    error: Optional[str] = None

class VisualOperation(BaseModel):
    type: str  # add_component, move_component, update_props, etc.
    component_type: Optional[str] = None
    component_id: Optional[str] = None
    props: Optional[Dict[str, Any]] = None
    parent_id: Optional[str] = None
    position: Optional[str] = None
    new_props: Optional[Dict[str, Any]] = None
    style_changes: Optional[Dict[str, Any]] = None

class VisualEditRequest(BaseModel):
    current_code: str
    operations: List[VisualOperation]

class GitHubRequest(BaseModel):
    project_name: str
    description: Optional[str] = ""
    private: Optional[bool] = False
    user_token: Optional[str] = None

class SupabaseRequest(BaseModel):
    project_id: str
    schema: Optional[Dict[str, Any]] = None
    auth_config: Optional[Dict[str, Any]] = None
    tables: Optional[List[str]] = None
    buckets: Optional[List[Dict[str, Any]]] = None

class MediaUploadResponse(BaseModel):
    success: bool
    file: Optional[Dict[str, Any]] = None
    image: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None