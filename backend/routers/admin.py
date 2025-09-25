from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Any
from services.admin_service import AdminService
from services.auth_service import AuthService
from models.admin import (
    DashboardData, UserManagement, ProjectManagement, 
    SystemLog, PlatformSettings
)
from models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])

async def require_admin(current_user: User, admin_service: Any):
    """Require admin privileges"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    is_admin = await admin_service.is_admin(current_user["id"])
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    admin_service: Any = Depends(),
    current_user: User = Depends(require_admin)
):
    """Get admin dashboard data"""
    try:
        dashboard_data = await admin_service.get_dashboard_data()
        await admin_service.log_system_event(
            "INFO", 
            f"Admin dashboard accessed by {current_user['email']}", 
            "admin", 
            current_user["id"]
        )
        return dashboard_data
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Dashboard error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")

@router.get("/users", response_model=List[UserManagement])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_service: Any = Depends(),
    current_user: User = Depends(require_admin)
):
    """Get users for management"""
    try:
        users = await admin_service.get_users_management(skip, limit)
        return users
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Users management error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load users")

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Update user active status"""
    try:
        success = await admin_service.update_user_status(user_id, is_active)
        if success:
            action = "activated" if is_active else "deactivated"
            await admin_service.log_system_event(
                "INFO", 
                f"User {user_id} {action} by admin {current_user['email']}", 
                "admin"
            )
            return {"success": True, "message": f"User {action} successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"User status update error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to update user status")

@router.get("/projects", response_model=List[ProjectManagement])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Get projects for management"""
    try:
        projects = await admin_service.get_projects_management(skip, limit)
        return projects
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Projects management error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load projects")

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Delete a project"""
    try:
        success = await admin_service.delete_project(project_id)
        if success:
            return {"success": True, "message": "Project deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Project deletion error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to delete project")

@router.get("/logs", response_model=List[SystemLog])
async def get_logs(
    level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Get system logs"""
    try:
        logs = await admin_service.get_system_logs(level, limit)
        return logs
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Logs retrieval error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load logs")

@router.get("/settings", response_model=PlatformSettings)
async def get_settings(
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Get platform settings"""
    try:
        settings = await admin_service.get_platform_settings()
        return settings
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Settings retrieval error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load settings")

@router.put("/settings")
async def update_settings(
    settings: PlatformSettings,
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Update platform settings"""
    try:
        success = await admin_service.update_platform_settings(settings)
        if success:
            return {"success": True, "message": "Settings updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update settings")
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Settings update error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@router.get("/analytics")
async def get_analytics(
    days: int = Query(30, ge=1, le=365),
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Get usage analytics"""
    try:
        analytics = await admin_service.get_usage_analytics(days)
        return analytics
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Analytics error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to load analytics")

@router.post("/users/{user_id}/make-admin")
async def make_admin(
    user_id: str,
    admin_service: AdminService = Depends(),
    current_user: User = Depends(require_admin)
):
    """Make a user admin"""
    try:
        admin_user = await admin_service.create_admin_user(
            user_id, 
            "admin", 
            current_user["id"]
        )
        await admin_service.log_system_event(
            "INFO", 
            f"User {user_id} made admin by {current_user['email']}", 
            "admin"
        )
        return {"success": True, "message": "User granted admin privileges"}
    except Exception as e:
        await admin_service.log_system_event("ERROR", f"Make admin error: {str(e)}", "admin")
        raise HTTPException(status_code=500, detail="Failed to grant admin privileges")