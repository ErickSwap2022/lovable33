import os
import aiofiles
import aiohttp
import asyncio
from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException

class DeploymentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.base_url = "https://deploy.lovable-clone.com"  # Simulate deployment service
    
    async def deploy_project(self, project_id: str, user_id: str, subdomain: str = None) -> Dict[str, Any]:
        """Deploy project to hosting service"""
        # Get project
        project = await self.db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check permissions
        if project["owner_id"] != user_id:
            user_role = next(
                (c["role"] for c in project.get("collaborators", []) if c["user_id"] == user_id),
                None
            )
            if user_role not in ["owner", "editor"]:
                raise HTTPException(status_code=403, detail="No deployment permissions")
        
        # Generate subdomain if not provided
        if not subdomain:
            subdomain = f"{project['name'].lower().replace(' ', '-')}-{project_id[:8]}"
        
        # Prepare deployment data
        deployment_data = {
            "project_id": project_id,
            "project_name": project["name"],
            "code": project.get("generated_code", ""),
            "subdomain": subdomain,
            "user_id": user_id
        }
        
        try:
            # Simulate deployment process
            deployment_url = await self._simulate_deployment(deployment_data)
            
            # Update project with deployment info
            await self.db.projects.update_one(
                {"id": project_id},
                {
                    "$set": {
                        "deployment_url": deployment_url,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Save deployment record
            deployment_record = {
                "project_id": project_id,
                "user_id": user_id,
                "deployment_url": deployment_url,
                "subdomain": subdomain,
                "status": "deployed",
                "deployed_at": datetime.utcnow()
            }
            
            await self.db.deployments.insert_one(deployment_record)
            
            return {
                "success": True,
                "deployment_url": deployment_url,
                "subdomain": subdomain,
                "message": "Project deployed successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")
    
    async def _simulate_deployment(self, deployment_data: Dict[str, Any]) -> str:
        """Simulate deployment process"""
        # Simulate deployment time
        await asyncio.sleep(2)
        
        # Generate deployment URL
        subdomain = deployment_data["subdomain"]
        deployment_url = f"https://{subdomain}.lovable-app.com"
        
        return deployment_url
    
    async def get_deployment_status(self, project_id: str) -> Dict[str, Any]:
        """Get deployment status for project"""
        deployment = await self.db.deployments.find_one(
            {"project_id": project_id},
            sort=[("deployed_at", -1)]
        )
        
        if not deployment:
            return {"status": "not_deployed"}
        
        return {
            "status": deployment["status"],
            "deployment_url": deployment["deployment_url"],
            "deployed_at": deployment["deployed_at"],
            "subdomain": deployment["subdomain"]
        }
    
    async def undeploy_project(self, project_id: str, user_id: str) -> bool:
        """Remove project deployment"""
        # Check permissions
        project = await self.db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if project["owner_id"] != user_id:
            raise HTTPException(status_code=403, detail="Only owner can undeploy")
        
        # Update deployment status
        await self.db.deployments.update_many(
            {"project_id": project_id},
            {"$set": {"status": "undeployed"}}
        )
        
        # Remove deployment URL from project
        await self.db.projects.update_one(
            {"id": project_id},
            {"$unset": {"deployment_url": ""}}
        )
        
        return True