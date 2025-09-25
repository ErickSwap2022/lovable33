import os
import uuid
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.admin import (
    AdminUser, UserStats, ProjectStats, SystemStats, DashboardData,
    UserManagement, ProjectManagement, SystemLog, PlatformSettings
)

class AdminService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.admin_collection = db.admin_users
        self.logs_collection = db.system_logs
        self.settings_collection = db.platform_settings

    async def create_admin_user(self, user_id: str, role: str = "admin", created_by: str = "system") -> AdminUser:
        """Create a new admin user"""
        admin_user = AdminUser(
            user_id=user_id,
            role=role,
            created_by=created_by
        )
        
        admin_dict = admin_user.dict()
        await self.admin_collection.insert_one(admin_dict)
        return admin_user

    async def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        admin = await self.admin_collection.find_one({
            "user_id": user_id,
            "is_active": True
        })
        return admin is not None

    async def get_dashboard_data(self) -> DashboardData:
        """Get comprehensive dashboard data"""
        # User statistics
        total_users = await self.db.users.count_documents({})
        active_users = await self.db.users.count_documents({"is_active": True})
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        new_users_today = await self.db.users.count_documents({
            "created_at": {"$gte": today}
        })
        new_users_week = await self.db.users.count_documents({
            "created_at": {"$gte": week_ago}
        })

        user_stats = UserStats(
            total_users=total_users,
            active_users=active_users,
            new_users_today=new_users_today,
            new_users_week=new_users_week
        )

        # Project statistics
        total_projects = await self.db.projects.count_documents({})
        projects_today = await self.db.projects.count_documents({
            "created_at": {"$gte": today}
        })
        projects_week = await self.db.projects.count_documents({
            "created_at": {"$gte": week_ago}
        })
        ai_generations = await self.db.code_generations.count_documents({})

        project_stats = ProjectStats(
            total_projects=total_projects,
            projects_today=projects_today,
            projects_week=projects_week,
            ai_generations=ai_generations
        )

        # System statistics
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        api_calls_today = await self.logs_collection.count_documents({
            "timestamp": {"$gte": today},
            "component": "api"
        })
        errors_today = await self.logs_collection.count_documents({
            "timestamp": {"$gte": today},
            "level": "ERROR"
        })

        system_stats = SystemStats(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            api_calls_today=api_calls_today,
            errors_today=errors_today
        )

        # Recent activities
        recent_activities = []
        recent_projects = await self.db.projects.find(
            {}, {"name": 1, "created_at": 1, "owner_id": 1}
        ).sort("created_at", -1).limit(10).to_list(length=None)
        
        for project in recent_projects:
            user = await self.db.users.find_one({"id": project["owner_id"]}, {"email": 1})
            recent_activities.append({
                "type": "project_created",
                "message": f"New project '{project['name']}' created by {user['email'] if user else 'Unknown'}",
                "timestamp": project["created_at"],
                "icon": "folder"
            })

        return DashboardData(
            user_stats=user_stats,
            project_stats=project_stats,
            system_stats=system_stats,
            recent_activities=recent_activities[:10]
        )

    async def get_users_management(self, skip: int = 0, limit: int = 50) -> List[UserManagement]:
        """Get users for management"""
        users = []
        
        # Aggregate users with project counts - only include users with 'id' field
        pipeline = [
            {
                "$match": {
                    "id": {"$exists": True},  # Only include users with UUID id field
                    "created_at": {"$exists": True}  # Only include users with created_at field
                }
            },
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "id",
                    "foreignField": "owner_id",
                    "as": "projects"
                }
            },
            {
                "$addFields": {
                    "projects_count": {"$size": "$projects"}
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        async for user in self.db.users.aggregate(pipeline):
            users.append(UserManagement(
                id=user["id"],
                email=user["email"],
                username=user.get("username"),
                created_at=user.get("created_at"),
                last_login=user.get("last_login"),
                projects_count=user["projects_count"],
                is_active=user.get("is_active", True),
                is_verified=user.get("is_verified", False)
            ))
        
        return users

    async def get_projects_management(self, skip: int = 0, limit: int = 50) -> List[ProjectManagement]:
        """Get projects for management"""
        projects = []
        
        # Aggregate projects with owner info
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "owner_id",
                    "foreignField": "id",
                    "as": "owner"
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        async for project in self.db.projects.aggregate(pipeline):
            owner = project["owner"][0] if project["owner"] else {}
            generated_code = project.get("generated_code", "") or ""  # Handle None values
            projects.append(ProjectManagement(
                id=project["id"],
                name=project["name"],
                owner_email=owner.get("email", "Unknown"),
                created_at=project["created_at"],
                updated_at=project["updated_at"],
                code_length=len(generated_code),
                is_public=project.get("is_public", False),
                initial_prompt=project.get("initial_prompt")
            ))
        
        return projects

    async def update_user_status(self, user_id: str, is_active: bool) -> bool:
        """Update user active status"""
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": {"is_active": is_active, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        result = await self.db.projects.delete_one({"id": project_id})
        if result.deleted_count > 0:
            # Also delete related code generations
            await self.db.code_generations.delete_many({"project_id": project_id})
            await self.log_system_event("INFO", f"Project {project_id} deleted by admin", "admin")
        return result.deleted_count > 0

    async def get_system_logs(self, level: Optional[str] = None, limit: int = 100) -> List[SystemLog]:
        """Get system logs"""
        query = {}
        if level:
            query["level"] = level
        
        logs = []
        async for log in self.logs_collection.find(query).sort("timestamp", -1).limit(limit):
            logs.append(SystemLog(**log))
        
        return logs

    async def log_system_event(self, level: str, message: str, component: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log system event"""
        log = SystemLog(
            level=level,
            message=message,
            component=component,
            user_id=user_id,
            metadata=metadata
        )
        
        await self.logs_collection.insert_one(log.dict())

    async def get_platform_settings(self) -> PlatformSettings:
        """Get platform settings"""
        settings = await self.settings_collection.find_one({})
        if settings:
            return PlatformSettings(**settings)
        else:
            # Create default settings
            default_settings = PlatformSettings()
            await self.settings_collection.insert_one(default_settings.dict())
            return default_settings

    async def update_platform_settings(self, settings: PlatformSettings) -> bool:
        """Update platform settings"""
        result = await self.settings_collection.replace_one(
            {},
            settings.dict(),
            upsert=True
        )
        await self.log_system_event("INFO", "Platform settings updated", "admin")
        return result.acknowledged

    async def get_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily user registrations
        daily_users = []
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        async for day in self.db.users.aggregate(pipeline):
            daily_users.append({
                "date": day["_id"],
                "count": day["count"]
            })

        # Daily project creation
        daily_projects = []
        async for day in self.db.projects.aggregate(pipeline):
            daily_projects.append({
                "date": day["_id"],
                "count": day["count"]
            })

        # AI generation stats
        ai_generations = []
        async for day in self.db.code_generations.aggregate(pipeline):
            ai_generations.append({
                "date": day["_id"],
                "count": day["count"]
            })

        return {
            "daily_users": daily_users,
            "daily_projects": daily_projects,
            "ai_generations": ai_generations
        }