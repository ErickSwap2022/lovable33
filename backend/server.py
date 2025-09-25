from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

# Import our custom modules
from services.ai_service import AIService
from models.project import Project, ProjectCreate, ChatMessage, GenerateCodeRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize AI Service
ai_service = AIService()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Original endpoints
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# New Lovable Clone Endpoints

@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate):
    """Create a new project"""
    try:
        project_dict = project_data.dict()
        project_obj = Project(**project_dict)
        
        # Insert into database
        result = await db.projects.insert_one(project_obj.dict())
        project_obj.id = str(result.inserted_id)
        
        return project_obj
    except Exception as e:
        logging.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    """Get all projects"""
    try:
        projects = await db.projects.find().to_list(100)
        return [Project(**project) for project in projects]
    except Exception as e:
        logging.error(f"Error fetching projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project"""
    try:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return Project(**project)
    except Exception as e:
        logging.error(f"Error fetching project: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch project")

@api_router.post("/generate-code")
async def generate_code(request: GenerateCodeRequest):
    """Generate code based on user prompt"""
    try:
        # Generate code using AI service
        generated_code = await ai_service.generate_code(request.prompt, request.session_id)
        
        # Save chat message to database
        message_data = {
            "session_id": request.session_id,
            "user_message": request.prompt,
            "ai_response": "I've generated your code! You can see it in the preview and edit it in the Code tab.",
            "generated_code": generated_code,
            "timestamp": datetime.utcnow()
        }
        
        await db.chat_messages.insert_one(message_data)
        
        return {
            "success": True,
            "code": generated_code,
            "message": "Code generated successfully"
        }
        
    except Exception as e:
        logging.error(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate code")

@api_router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(100)
        
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
        if message.type == "user":
            # Generate AI response
            ai_response = await ai_service.generate_response(message.content, session_id)
            
            # Save both user message and AI response
            user_message_data = {
                "session_id": session_id,
                "type": "user",
                "content": message.content,
                "timestamp": datetime.utcnow()
            }
            
            ai_message_data = {
                "session_id": session_id,
                "type": "assistant",
                "content": ai_response,
                "timestamp": datetime.utcnow()
            }
            
            await db.chat_messages.insert_many([user_message_data, ai_message_data])
            
            return {
                "success": True,
                "user_message": user_message_data,
                "ai_response": ai_message_data
            }
        else:
            # Just save the message
            message_data = {
                "session_id": session_id,
                **message.dict(),
                "timestamp": datetime.utcnow()
            }
            
            await db.chat_messages.insert_one(message_data)
            
            return {
                "success": True,
                "message": message_data
            }
            
    except Exception as e:
        logging.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

# Include the router in the main app
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()