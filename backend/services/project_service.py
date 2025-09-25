import os
import json
import uuid
import aiofiles
from typing import List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from models.project_extended import Project, ProjectVersion, ProjectCollaborator

class ProjectService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_project(self, project_data: dict, owner_id: str) -> Project:
        """Create a new project"""
        project_data["owner_id"] = owner_id
        
        # If template_id is provided, get template code
        if project_data.get("template_id"):
            template = await self.db.templates.find_one({"id": project_data["template_id"]})
            if template:
                project_data["generated_code"] = template["code"]
        
        # Add initial collaborator (owner)
        project_data["collaborators"] = [
            ProjectCollaborator(user_id=owner_id, role="owner").dict()
        ]
        
        # Create initial version
        if project_data.get("generated_code"):
            initial_version = ProjectVersion(
                version="1.0.0",
                code=project_data["generated_code"],
                description="Initial version"
            )
            project_data["versions"] = [initial_version.dict()]
        
        project = Project(**project_data)
        result = await self.db.projects.insert_one(project.dict())
        project.id = str(result.inserted_id)
        
        return project
    
    async def get_user_projects(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get projects for a specific user"""
        projects = await self.db.projects.find({
            "$or": [
                {"owner_id": user_id},
                {"collaborators.user_id": user_id}
            ]
        }).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [Project(**project) for project in projects]
    
    async def get_public_projects(self, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get public projects"""
        projects = await self.db.projects.find({
            "is_public": True
        }).sort([
            ("is_featured", -1),
            ("likes_count", -1),
            ("created_at", -1)
        ]).skip(skip).limit(limit).to_list(limit)
        
        return [Project(**project) for project in projects]
    
    async def get_project_by_id(self, project_id: str, user_id: str = None) -> Project:
        """Get project by ID with access control"""
        project = await self.db.projects.find_one({"id": project_id})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_obj = Project(**project)
        
        # Check access permissions
        if not project_obj.is_public:
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Check if user has access
            has_access = (
                project_obj.owner_id == user_id or
                any(c.user_id == user_id for c in project_obj.collaborators)
            )
            
            if not has_access:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Increment view count
        await self.db.projects.update_one(
            {"id": project_id},
            {"$inc": {"views_count": 1}}
        )
        
        return project_obj
    
    async def update_project(self, project_id: str, update_data: dict, user_id: str) -> Project:
        """Update project"""
        project = await self.get_project_by_id(project_id, user_id)
        
        # Check if user can edit
        if project.owner_id != user_id:
            # Check if user is an editor
            user_role = next(
                (c.role for c in project.collaborators if c.user_id == user_id),
                None
            )
            if user_role not in ["owner", "editor"]:
                raise HTTPException(status_code=403, detail="No edit permissions")
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.projects.update_one(
            {"id": project_id},
            {"$set": update_data}
        )
        
        return await self.get_project_by_id(project_id, user_id)
    
    async def delete_project(self, project_id: str, user_id: str):
        """Delete project (owner only)"""
        project = await self.get_project_by_id(project_id, user_id)
        
        if project.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only owner can delete project")
        
        await self.db.projects.delete_one({"id": project_id})
        return True
    
    async def fork_project(self, project_id: str, user_id: str, fork_name: str = None) -> Project:
        """Fork a project"""
        original_project = await self.get_project_by_id(project_id)
        
        if not original_project.is_public and original_project.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot fork private project")
        
        # Create forked project
        fork_data = {
            "name": fork_name or f"Fork of {original_project.name}",
            "description": f"Forked from {original_project.name}",
            "generated_code": original_project.generated_code,
            "tech_stack": original_project.tech_stack,
            "is_public": False,  # Forks start as private
            "tags": original_project.tags
        }
        
        fork = await self.create_project(fork_data, user_id)
        
        # Increment fork count on original
        await self.db.projects.update_one(
            {"id": project_id},
            {"$inc": {"forks_count": 1}}
        )
        
        return fork
    
    async def add_collaborator(self, project_id: str, collaborator_email: str, role: str, owner_id: str):
        """Add collaborator to project"""
        project = await self.get_project_by_id(project_id, owner_id)
        
        if project.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Only owner can add collaborators")
        
        # Find user by email
        user = await self.db.users.find_one({"email": collaborator_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already a collaborator
        if any(c["user_id"] == user["id"] for c in project.collaborators):
            raise HTTPException(status_code=400, detail="User is already a collaborator")
        
        # Add collaborator
        new_collaborator = ProjectCollaborator(user_id=user["id"], role=role)
        
        await self.db.projects.update_one(
            {"id": project_id},
            {"$push": {"collaborators": new_collaborator.dict()}}
        )
        
        return True
    
    async def save_project_version(self, project_id: str, code: str, version_desc: str, user_id: str):
        """Save a new version of the project"""
        project = await self.get_project_by_id(project_id, user_id)
        
        # Check edit permissions
        if project.owner_id != user_id:
            user_role = next(
                (c.role for c in project.collaborators if c.user_id == user_id),
                None
            )
            if user_role not in ["owner", "editor"]:
                raise HTTPException(status_code=403, detail="No edit permissions")
        
        # Create new version
        version_number = f"1.{len(project.versions)}.0"
        new_version = ProjectVersion(
            version=version_number,
            code=code,
            description=version_desc or f"Version {version_number}"
        )
        
        # Update project
        await self.db.projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "generated_code": code,
                    "current_version": version_number,
                    "updated_at": datetime.utcnow()
                },
                "$push": {"versions": new_version.dict()}
            }
        )
        
        return new_version