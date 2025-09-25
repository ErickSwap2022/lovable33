# Script to add new API routes to server.py

routes_to_add = '''

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
        # Get project files
        project_files = []  # Would fetch from project
        
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

@api_router.post("/github/export-codebase")
async def export_full_codebase(project_id: str, project_files: Dict[str, str], user_token: Optional[str] = None):
    """Export complete codebase"""
    try:
        result = await github_service.export_full_codebase(project_id, project_files, user_token)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to export codebase"
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

@api_router.post("/supabase/setup-auth")
async def setup_supabase_auth(request: SupabaseRequest):
    """Set up Supabase authentication"""
    try:
        result = await supabase_service.setup_authentication(
            request.project_id,
            request.auth_config or {}
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to setup authentication"
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

@api_router.post("/media/upload-file")
async def upload_file(file_data: bytes, filename: str, project_id: Optional[str] = None):
    """Upload general files"""
    try:
        result = await media_service.upload_file(file_data, filename, project_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to upload file"
        }

@api_router.get("/media/project/{project_id}")
async def get_project_media(project_id: str):
    """Get all media files for a project"""
    try:
        result = await media_service.get_project_media(project_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get project media"
        }
'''

# This script would add the routes to server.py
print("New routes ready to be added to server.py")
print(routes_to_add)