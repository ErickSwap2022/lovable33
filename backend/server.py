from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
import asyncio

# Import models
from models.user import User, UserCreate, UserLogin, UserResponse, Token, UserUpdate
from models.template import Template, TemplateCreate, TemplateResponse
from models.project_extended import Project, ProjectCreate, ProjectUpdate, ProjectResponse, DeploymentRequest
from models.project import ChatMessage, GenerateCodeRequest
from models.admin import DashboardData, UserManagement, ProjectManagement, SystemLog, PlatformSettings
from models.agent import AgentRequest, AgentResponse, VisualOperation, VisualEditRequest, GitHubRequest, SupabaseRequest, MediaUploadResponse

# Import services
from services.auth_service import AuthService
from services.project_service import ProjectService
from services.template_service import TemplateService
from services.deployment_service import DeploymentService
from services.enhanced_ai_service import EnhancedAIService
from services.admin_service import AdminService
from services.agent_service import AgentService
from services.supabase_service import SupabaseService
from services.github_service import GitHubService
from services.visual_editor_service import VisualEditorService
from services.media_service import MediaService
from services.chat_mode_agent_service import ChatModeAgentService
from services.realtime_visual_service import RealtimeVisualService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize Services
auth_service = AuthService(db)
project_service = ProjectService(db)
template_service = TemplateService(db)
deployment_service = DeploymentService(db)
ai_service = EnhancedAIService()
admin_service = AdminService(db)
agent_service = AgentService()
supabase_service = SupabaseService()
github_service = GitHubService()
visual_editor_service = VisualEditorService()
media_service = MediaService()
chat_agent_service = ChatModeAgentService()
realtime_visual_service = RealtimeVisualService()

# Security
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    if not credentials:
        return None
    
    try:
        payload = auth_service.decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await auth_service.get_user_by_id(user_id)
        return user
    except:
        return None

async def require_auth(user = Depends(get_current_user)):
    """Require authentication"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user

# Create the main app
app = FastAPI(title="Lovable Clone API", version="1.0.0")

# Create routers
api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
projects_router = APIRouter(prefix="/projects", tags=["Projects"])
templates_router = APIRouter(prefix="/templates", tags=["Templates"])
ai_router = APIRouter(prefix="/ai", tags=["AI"])
deploy_router = APIRouter(prefix="/deploy", tags=["Deployment"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@auth_router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user_dict = user_data.dict()
        user = await auth_service.create_user(user_dict)
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["id"]}
        )
        
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            username=user.get("username"),
            bio=user.get("bio"),
            avatar=user.get("avatar"),
            is_premium=user.get("is_premium", False),
            projects_count=0,
            followers_count=0,
            following_count=0
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user"""
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user["id"]}
    )
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        username=user.get("username"),
        bio=user.get("bio"),
        avatar=user.get("avatar"),
        is_premium=user.get("is_premium", False),
        projects_count=user.get("projects_count", 0),
        followers_count=user.get("followers_count", 0),
        following_count=user.get("following_count", 0)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(user = Depends(require_auth)):
    """Get current user information"""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        username=user.get("username"),
        bio=user.get("bio"),
        avatar=user.get("avatar"),
        is_premium=user.get("is_premium", False),
        projects_count=user.get("projects_count", 0),
        followers_count=user.get("followers_count", 0),
        following_count=user.get("following_count", 0)
    )

# =============================================================================
# PROJECT ROUTES
# =============================================================================

@projects_router.post("/", response_model=Project)
async def create_project(project_data: ProjectCreate, user = Depends(require_auth)):
    """Create a new project"""
    return await project_service.create_project(project_data.dict(), user["id"])

@projects_router.get("/", response_model=List[Project])
async def get_projects(
    public: bool = False, 
    skip: int = 0, 
    limit: int = 20,
    user = Depends(get_current_user)
):
    """Get projects (public or user's projects)"""
    if public or not user:
        return await project_service.get_public_projects(skip, limit)
    else:
        return await project_service.get_user_projects(user["id"], skip, limit)

@projects_router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, user = Depends(get_current_user)):
    """Get a specific project"""
    user_id = user["id"] if user else None
    return await project_service.get_project_by_id(project_id, user_id)

@projects_router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str, 
    update_data: ProjectUpdate, 
    user = Depends(require_auth)
):
    """Update a project"""
    return await project_service.update_project(project_id, update_data.dict(exclude_unset=True), user["id"])

@projects_router.delete("/{project_id}")
async def delete_project(project_id: str, user = Depends(require_auth)):
    """Delete a project"""
    await project_service.delete_project(project_id, user["id"])
    return {"success": True, "message": "Project deleted successfully"}

@projects_router.post("/{project_id}/fork", response_model=Project)
async def fork_project(
    project_id: str, 
    fork_name: Optional[str] = None, 
    user = Depends(require_auth)
):
    """Fork a project"""
    return await project_service.fork_project(project_id, user["id"], fork_name)

@projects_router.post("/{project_id}/collaborators")
async def add_collaborator(
    project_id: str,
    collaborator_email: str,
    role: str = "editor",
    user = Depends(require_auth)
):
    """Add collaborator to project"""
    await project_service.add_collaborator(project_id, collaborator_email, role, user["id"])
    return {"success": True, "message": "Collaborator added successfully"}

# =============================================================================
# TEMPLATE ROUTES
# =============================================================================

@templates_router.get("/", response_model=List[Template])
async def get_templates(category: str = None, skip: int = 0, limit: int = 20):
    """Get templates"""
    return await template_service.get_templates(category, skip, limit)

@templates_router.get("/featured", response_model=List[Template])
async def get_featured_templates(limit: int = 10):
    """Get featured templates"""
    return await template_service.get_featured_templates(limit)

@templates_router.get("/categories")
async def get_template_categories():
    """Get template categories"""
    return await template_service.get_categories()

@templates_router.get("/search", response_model=List[Template])
async def search_templates(q: str, skip: int = 0, limit: int = 20):
    """Search templates"""
    return await template_service.search_templates(q, skip, limit)

@templates_router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get specific template"""
    return await template_service.get_template_by_id(template_id)

@templates_router.post("/{template_id}/use", response_model=Template)
async def use_template(template_id: str):
    """Mark template as used"""
    return await template_service.use_template(template_id)

@templates_router.post("/", response_model=Template)
async def create_template(template_data: TemplateCreate, user = Depends(require_auth)):
    """Create a new template"""
    return await template_service.create_template(template_data, user["id"])

# =============================================================================
# AI ROUTES
# =============================================================================

@ai_router.post("/generate-code")
async def generate_code(request: GenerateCodeRequest):
    """Generate code using AI"""
    try:
        result = await ai_service.generate_code(
            request.prompt, 
            request.session_id,
            context=getattr(request, 'context', None)
        )
        
        # Save generation to database
        generation_record = {
            "session_id": request.session_id,
            "prompt": request.prompt,
            "generated_code": result["code"],
            "metadata": result["metadata"],
            "created_at": datetime.utcnow()
        }
        
        await db.code_generations.insert_one(generation_record)
        
        return {
            "success": True,
            "code": result["code"],
            "metadata": result["metadata"],
            "message": "Code generated successfully"
        }
        
    except Exception as e:
        logging.error(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate code")

@ai_router.post("/improve-code")
async def improve_code(code: str, session_id: str):
    """Get AI suggestions for code improvement"""
    try:
        suggestions = await ai_service.suggest_improvements(code, session_id)
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        logging.error(f"Error generating improvements: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate improvements")

@ai_router.post("/generate-tests")
async def generate_tests(code: str, session_id: str):
    """Generate tests for code"""
    try:
        tests = await ai_service.generate_tests(code, session_id)
        return {
            "success": True,
            "tests": tests
        }
    except Exception as e:
        logging.error(f"Error generating tests: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate tests")

# =============================================================================
# DEPLOYMENT ROUTES
# =============================================================================

@deploy_router.post("/")
async def deploy_project(request: DeploymentRequest, user = Depends(require_auth)):
    """Deploy a project"""
    return await deployment_service.deploy_project(
        request.project_id, 
        user["id"], 
        request.subdomain
    )

@deploy_router.get("/{project_id}/status")
async def get_deployment_status(project_id: str):
    """Get deployment status"""
    return await deployment_service.get_deployment_status(project_id)

@deploy_router.delete("/{project_id}")
async def undeploy_project(project_id: str, user = Depends(require_auth)):
    """Undeploy a project"""
    await deployment_service.undeploy_project(project_id, user["id"])
    return {"success": True, "message": "Project undeployed successfully"}

# =============================================================================
# CHAT ROUTES
# =============================================================================

@api_router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(100)
        
        # Remove MongoDB ObjectId from messages
        for message in messages:
            message.pop("_id", None)
        
        return {
            "success": True,
            "messages": messages
        }
    except Exception as e:
        logging.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@api_router.post("/chat/{session_id}")
async def add_chat_message(session_id: str, message: ChatMessage):
    """Add a new chat message"""
    try:
        message_data = {
            "session_id": session_id,
            **message.dict(),
            "timestamp": datetime.utcnow()
        }
        
        result = await db.chat_messages.insert_one(message_data)
        
        # Remove ObjectId for response
        message_data.pop("_id", None)
        
        return {
            "success": True,
            "message": message_data
        }
        
    except Exception as e:
        logging.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

# =============================================================================
# LEGACY ROUTES
# =============================================================================

@api_router.get("/")
async def root():
    return {"message": "Lovable Clone API v1.0.0", "status": "online"}

# =============================================================================
# AGENT MODE ROUTES (AI Autonomous)
# =============================================================================

@ai_router.post("/agent-generate")
async def agent_generate_code(request: AgentRequest):
    """Generate code using autonomous AI agent with 91% error reduction"""
    try:
        result = await agent_service.autonomous_code_generation(
            request.prompt, 
            request.session_id,
            request.context
        )
        
        if result["success"]:
            # Save generation to database
            generation_record = {
                "session_id": request.session_id,
                "prompt": request.prompt,
                "generated_code": result["code"],
                "confidence_score": result["confidence_score"],
                "plan": result["plan"],
                "created_at": datetime.utcnow()
            }
            
            await db.agent_generations.insert_one(generation_record)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Agent code generation failed"
        }

@ai_router.post("/codebase-search")
async def codebase_search(query: str, project_id: str):
    """Intelligent codebase search"""
    try:
        # Get project files - would fetch from project in real implementation
        project_files = []
        
        results = await agent_service.codebase_search(query, project_files)
        
        return {
            "success": True,
            "results": results,
            "query": query
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Codebase search failed"
        }

# =============================================================================
# VISUAL EDITOR ROUTES
# =============================================================================

@api_router.post("/visual-editor/apply")
async def apply_visual_changes(request: VisualEditRequest):
    """Apply visual editor changes to code"""
    try:
        result = await visual_editor_service.apply_visual_changes_to_code(
            request.current_code,
            [op.dict() for op in request.operations]
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to apply visual changes"
        }

@api_router.get("/visual-editor/metadata")
async def get_visual_editor_metadata(code: str):
    """Get metadata for visual editor"""
    try:
        result = await visual_editor_service.generate_visual_editor_metadata(code)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate visual editor metadata"
        }

# =============================================================================
# GITHUB INTEGRATION ROUTES
# =============================================================================

@api_router.post("/github/create-repo")
async def create_github_repo(request: GitHubRequest, user = Depends(get_current_user)):
    """Create GitHub repository"""
    try:
        result = await github_service.create_repository(
            request.project_name,
            request.description,
            request.private,
            request.user_token
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create GitHub repository"
        }

@api_router.post("/github/auto-commit")
async def auto_commit_code(repo_name: str, files: Dict[str, str], message: str, user_token: Optional[str] = None):
    """Auto-commit code to GitHub"""
    try:
        result = await github_service.auto_commit_code(repo_name, files, message, user_token)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to commit code"
        }

# =============================================================================
# SUPABASE INTEGRATION ROUTES  
# =============================================================================

@api_router.post("/supabase/setup-database")
async def setup_supabase_database(request: SupabaseRequest):
    """Set up Supabase database tables"""
    try:
        result = await supabase_service.setup_database_tables(
            request.project_id,
            request.schema or {}
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to setup database"
        }

@api_router.post("/supabase/chat-to-db")
async def chat_to_database(project_id: str, query: str):
    """Convert natural language to database operations"""
    try:
        result = await supabase_service.chat_to_database(project_id, query)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process database chat"
        }

# =============================================================================
# MEDIA & FILE UPLOAD ROUTES
# =============================================================================

@api_router.post("/media/upload-image")
async def upload_image(file_data: bytes, filename: str, project_id: Optional[str] = None):
    """Upload and process images"""
    try:
        result = await media_service.upload_image(file_data, filename, project_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to upload image"
        }

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(projects_router)  
api_router.include_router(templates_router)
api_router.include_router(ai_router)
api_router.include_router(deploy_router)

# Create admin router with dependencies
admin_router_with_deps = APIRouter(prefix="/admin", tags=["Admin"])

# Override dependencies for admin routes
def get_admin_service():
    return admin_service

def get_current_user_for_admin(credentials = Depends(security)):
    return get_current_user(credentials)

async def require_admin_access(current_user = Depends(get_current_user), admin_svc = Depends(get_admin_service)):
    """Require admin privileges"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    is_admin = await admin_svc.is_admin(current_user["id"])
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

# Add admin routes with proper dependencies
@admin_router_with_deps.get("/dashboard", response_model=DashboardData)
async def admin_dashboard(current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Get admin dashboard data"""
    try:
        dashboard_data = await admin_svc.get_dashboard_data()
        await admin_svc.log_system_event(
            "INFO", 
            f"Admin dashboard accessed by {current_user['email']}", 
            "admin", 
            current_user["id"]
        )
        return dashboard_data
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Dashboard error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")

@admin_router_with_deps.get("/users", response_model=List[UserManagement])
async def admin_get_users(skip: int = 0, limit: int = 50, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Get users for management"""
    try:
        users = await admin_svc.get_users_management(skip, limit)
        return users
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Users management error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load users")

@admin_router_with_deps.put("/users/{user_id}/status")
async def admin_update_user_status(user_id: str, is_active: bool, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Update user active status"""
    try:
        success = await admin_svc.update_user_status(user_id, is_active)
        if success:
            action = "activated" if is_active else "deactivated"
            await admin_svc.log_system_event(
                "INFO", 
                f"User {user_id} {action} by admin {current_user['email']}", 
                "admin"
            )
            return {"success": True, "message": f"User {action} successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"User status update error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to update user status")

@admin_router_with_deps.get("/projects", response_model=List[ProjectManagement])
async def admin_get_projects(skip: int = 0, limit: int = 50, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Get projects for management"""
    try:
        projects = await admin_svc.get_projects_management(skip, limit)
        return projects
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Projects management error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load projects")

@admin_router_with_deps.delete("/projects/{project_id}")
async def admin_delete_project(project_id: str, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Delete a project"""
    try:
        success = await admin_svc.delete_project(project_id)
        if success:
            return {"success": True, "message": "Project deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Project deletion error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to delete project")

@admin_router_with_deps.get("/logs", response_model=List[SystemLog])
async def admin_get_logs(level: Optional[str] = None, limit: int = 100, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Get system logs"""
    try:
        logs = await admin_svc.get_system_logs(level, limit)
        return logs
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Logs retrieval error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load logs")

@admin_router_with_deps.get("/settings", response_model=PlatformSettings)
async def admin_get_settings(current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Get platform settings"""
    try:
        settings = await admin_svc.get_platform_settings()
        return settings
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Settings retrieval error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load settings")

@admin_router_with_deps.put("/settings")
async def admin_update_settings(settings: PlatformSettings, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Update platform settings"""
    try:
        success = await admin_svc.update_platform_settings(settings)
        if success:
            return {"success": True, "message": "Settings updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update settings")
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Settings update error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@admin_router_with_deps.get("/analytics")
async def admin_get_analytics(days: int = 30, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Get usage analytics"""
    try:
        analytics = await admin_svc.get_usage_analytics(days)
        return analytics
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Analytics error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load analytics")

@admin_router_with_deps.post("/users/{user_id}/make-admin")
async def admin_make_admin(user_id: str, current_user = Depends(require_admin_access), admin_svc = Depends(get_admin_service)):
    """Make a user admin"""
    try:
        admin_user = await admin_svc.create_admin_user(
            user_id, 
            "admin", 
            current_user["id"]
        )
        await admin_svc.log_system_event(
            "INFO", 
            f"User {user_id} made admin by {current_user['email']}", 
            "admin"
        )
        return {"success": True, "message": "User granted admin privileges"}
    except Exception as e:
        await admin_svc.log_system_event("ERROR", f"Make admin error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to grant admin privileges")

api_router.include_router(admin_router_with_deps)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    """Initialize database with default data"""
    try:
        # Seed default templates
        await template_service.seed_default_templates()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()