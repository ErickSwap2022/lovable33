from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role: str = "admin"  # admin, super_admin
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    is_active: bool = True

class UserStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_week: int

class ProjectStats(BaseModel):
    total_projects: int
    projects_today: int
    projects_week: int
    ai_generations: int

class SystemStats(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    api_calls_today: int
    errors_today: int

class DashboardData(BaseModel):
    user_stats: UserStats
    project_stats: ProjectStats
    system_stats: SystemStats
    recent_activities: List[Dict[str, Any]]

class UserManagement(BaseModel):
    id: str
    email: str
    username: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    projects_count: int
    is_active: bool
    is_verified: bool

class ProjectManagement(BaseModel):
    id: str
    name: str
    owner_email: str
    created_at: datetime
    updated_at: datetime
    code_length: int
    is_public: bool
    initial_prompt: Optional[str]

class SystemLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    level: str  # INFO, WARNING, ERROR
    message: str
    component: str  # frontend, backend, ai_service
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PlatformSettings(BaseModel):
    ai_model: str = "claude-3-5-sonnet-20241022"
    ai_provider: str = "anthropic"
    max_generations_per_user_day: int = 50
    max_projects_per_user: int = 100
    enable_user_registration: bool = True
    maintenance_mode: bool = False
    announcement: Optional[str] = None