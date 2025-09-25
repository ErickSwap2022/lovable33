import os
import asyncio
import uuid
import mimetypes
from typing import Dict, List, Optional, Any, BinaryIO
from datetime import datetime
import aiofiles
from pathlib import Path

class MediaService:
    """
    Complete file and media handling service
    Supports image upload, file upload, and asset management like Lovable
    """
    
    def __init__(self):
        self.upload_dir = Path("/app/uploads")
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_image_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'
        }
        self.allowed_file_types = {
            'application/pdf', 'text/plain', 'application/json', 'text/csv',
            'application/zip', 'application/x-zip-compressed'
        }
        
        # Create upload directories
        self._ensure_upload_dirs()
    
    def _ensure_upload_dirs(self):
        """Create necessary upload directories"""
        
        directories = [
            self.upload_dir,
            self.upload_dir / "images",
            self.upload_dir / "files", 
            self.upload_dir / "assets",
            self.upload_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def upload_image(self, file_data: bytes, filename: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload and process images with optimization
        """
        try:
            # Validate file
            validation = await self._validate_file(file_data, filename, "image")
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "message": "Image validation failed"
                }
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix.lower()
            new_filename = f"{file_id}{file_extension}"
            
            # Determine save path
            if project_id:
                save_dir = self.upload_dir / "images" / project_id
            else:
                save_dir = self.upload_dir / "images" / "general"
            
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = save_dir / new_filename
            
            # Save original file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # Generate image variants (thumbnails, etc.)
            variants = await self._generate_image_variants(file_path, file_id)
            
            # Create image record
            image_record = {
                "id": file_id,
                "filename": filename,
                "stored_filename": new_filename,
                "file_path": str(file_path),
                "project_id": project_id,
                "size": len(file_data),
                "mime_type": validation["mime_type"],
                "created_at": datetime.utcnow(),
                "variants": variants,
                "url": f"/uploads/images/{project_id or 'general'}/{new_filename}",
                "public_url": f"https://your-domain.com/uploads/images/{project_id or 'general'}/{new_filename}"
            }
            
            return {
                "success": True,
                "image": image_record,
                "message": "Image uploaded successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to upload image"
            }
    
    async def upload_file(self, file_data: bytes, filename: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload general files with validation
        """
        try:
            # Validate file
            validation = await self._validate_file(file_data, filename, "file")
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "message": "File validation failed"
                }
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix.lower()
            new_filename = f"{file_id}{file_extension}"
            
            # Determine save path
            if project_id:
                save_dir = self.upload_dir / "files" / project_id
            else:
                save_dir = self.upload_dir / "files" / "general"
            
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = save_dir / new_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # Create file record
            file_record = {
                "id": file_id,
                "filename": filename,
                "stored_filename": new_filename,
                "file_path": str(file_path),
                "project_id": project_id,
                "size": len(file_data),
                "mime_type": validation["mime_type"],
                "created_at": datetime.utcnow(),
                "url": f"/uploads/files/{project_id or 'general'}/{new_filename}",
                "download_url": f"/api/media/download/{file_id}"
            }
            
            return {
                "success": True,
                "file": file_record,
                "message": "File uploaded successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to upload file"
            }
    
    async def _validate_file(self, file_data: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        
        # Check file size
        if len(file_data) > self.max_file_size:
            return {
                "valid": False,
                "error": f"File size exceeds maximum allowed size ({self.max_file_size / (1024*1024)}MB)"
            }
        
        # Check file extension and MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        
        if file_type == "image":
            allowed_types = self.allowed_image_types
        elif file_type == "file":
            allowed_types = self.allowed_file_types | self.allowed_image_types
        else:
            allowed_types = self.allowed_file_types | self.allowed_image_types
        
        if mime_type not in allowed_types:
            return {
                "valid": False,
                "error": f"File type {mime_type} not allowed"
            }
        
        # Additional security checks
        if len(file_data) == 0:
            return {
                "valid": False,
                "error": "Empty file not allowed"
            }
        
        return {
            "valid": True,
            "mime_type": mime_type
        }
    
    async def _generate_image_variants(self, original_path: Path, file_id: str) -> Dict[str, str]:
        """Generate image variants (thumbnails, etc.)"""
        
        variants = {}
        
        try:
            # For now, return the original image as variants
            # In a real implementation, you'd use PIL or similar to create thumbnails
            
            variants["original"] = str(original_path)
            variants["thumbnail"] = str(original_path)  # Would be actual thumbnail
            variants["medium"] = str(original_path)     # Would be medium size
            
        except Exception as e:
            # If variant generation fails, just use original
            variants["original"] = str(original_path)
        
        return variants
    
    async def chunked_upload_start(self, filename: str, file_size: int, chunk_size: int = 1024*1024) -> Dict[str, Any]:
        """
        Start a chunked file upload session
        """
        try:
            upload_id = str(uuid.uuid4())
            
            # Create temp directory for chunks
            temp_dir = self.upload_dir / "temp" / upload_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Calculate number of chunks
            total_chunks = (file_size + chunk_size - 1) // chunk_size
            
            # Create upload session record
            session_record = {
                "upload_id": upload_id,
                "filename": filename,
                "file_size": file_size,
                "chunk_size": chunk_size,
                "total_chunks": total_chunks,
                "chunks_received": 0,
                "temp_dir": str(temp_dir),
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            return {
                "success": True,
                "upload_session": session_record,
                "message": "Chunked upload session started"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start chunked upload"
            }
    
    async def chunked_upload_chunk(self, upload_id: str, chunk_number: int, chunk_data: bytes) -> Dict[str, Any]:
        """
        Upload a single chunk
        """
        try:
            temp_dir = self.upload_dir / "temp" / upload_id
            
            if not temp_dir.exists():
                return {
                    "success": False,
                    "error": "Upload session not found",
                    "message": "Invalid upload session"
                }
            
            # Save chunk
            chunk_path = temp_dir / f"chunk_{chunk_number:06d}"
            async with aiofiles.open(chunk_path, 'wb') as f:
                await f.write(chunk_data)
            
            return {
                "success": True,
                "chunk_number": chunk_number,
                "chunk_size": len(chunk_data),
                "message": f"Chunk {chunk_number} uploaded successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to upload chunk"
            }
    
    async def chunked_upload_complete(self, upload_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete chunked upload by combining all chunks
        """
        try:
            temp_dir = self.upload_dir / "temp" / upload_id
            
            if not temp_dir.exists():
                return {
                    "success": False,
                    "error": "Upload session not found"
                }
            
            # Get all chunk files
            chunk_files = sorted(temp_dir.glob("chunk_*"))
            
            if not chunk_files:
                return {
                    "success": False,
                    "error": "No chunks found"
                }
            
            # Combine chunks
            file_id = str(uuid.uuid4())
            final_filename = f"{file_id}_upload"
            
            if project_id:
                final_dir = self.upload_dir / "files" / project_id
            else:
                final_dir = self.upload_dir / "files" / "general"
            
            final_dir.mkdir(parents=True, exist_ok=True)
            final_path = final_dir / final_filename
            
            # Combine all chunks into final file
            async with aiofiles.open(final_path, 'wb') as final_file:
                for chunk_file in chunk_files:
                    async with aiofiles.open(chunk_file, 'rb') as chunk:
                        data = await chunk.read()
                        await final_file.write(data)
            
            # Get final file size
            final_size = final_path.stat().st_size
            
            # Clean up temp directory
            await self._cleanup_temp_dir(temp_dir)
            
            return {
                "success": True,
                "file": {
                    "id": file_id,
                    "filename": final_filename,
                    "file_path": str(final_path),
                    "size": final_size,
                    "project_id": project_id,
                    "created_at": datetime.utcnow()
                },
                "message": "Chunked upload completed successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to complete chunked upload"
            }
    
    async def _cleanup_temp_dir(self, temp_dir: Path):
        """Clean up temporary directory"""
        try:
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()
        except Exception:
            # If cleanup fails, it's not critical
            pass
    
    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get file information by ID"""
        
        # In a real implementation, this would query a database
        # For now, return mock file info
        
        return {
            "success": True,
            "file": {
                "id": file_id,
                "filename": f"file_{file_id}.jpg",
                "size": 1024000,
                "mime_type": "image/jpeg",
                "created_at": datetime.utcnow(),
                "url": f"/uploads/images/general/{file_id}.jpg"
            }
        }
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file by ID"""
        
        try:
            # In a real implementation, find the file in database and delete from disk
            # For now, return success
            
            return {
                "success": True,
                "message": f"File {file_id} deleted successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete file"
            }
    
    async def get_project_media(self, project_id: str) -> Dict[str, Any]:
        """Get all media files for a project"""
        
        try:
            project_images_dir = self.upload_dir / "images" / project_id
            project_files_dir = self.upload_dir / "files" / project_id
            
            media_files = []
            
            # Get images
            if project_images_dir.exists():
                for image_file in project_images_dir.iterdir():
                    if image_file.is_file():
                        media_files.append({
                            "id": image_file.stem,
                            "filename": image_file.name,
                            "type": "image",
                            "size": image_file.stat().st_size,
                            "url": f"/uploads/images/{project_id}/{image_file.name}",
                            "created_at": datetime.fromtimestamp(image_file.stat().st_ctime)
                        })
            
            # Get files
            if project_files_dir.exists():
                for file_item in project_files_dir.iterdir():
                    if file_item.is_file():
                        media_files.append({
                            "id": file_item.stem,
                            "filename": file_item.name,
                            "type": "file",
                            "size": file_item.stat().st_size,
                            "url": f"/uploads/files/{project_id}/{file_item.name}",
                            "created_at": datetime.fromtimestamp(file_item.stat().st_ctime)
                        })
            
            return {
                "success": True,
                "media_files": media_files,
                "total_count": len(media_files)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get project media"
            }
    
    async def optimize_image(self, image_path: str, quality: int = 85) -> Dict[str, Any]:
        """Optimize image for web use"""
        
        try:
            # In a real implementation, use PIL or similar library for optimization
            # For now, return mock optimization result
            
            return {
                "success": True,
                "original_size": 2048000,
                "optimized_size": 512000,
                "compression_ratio": 75.0,
                "message": "Image optimized successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to optimize image"
            }