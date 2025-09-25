import os
import shutil
import mimetypes
from uuid import uuid4
from datetime import datetime
from typing import Dict, Optional, BinaryIO
from pathlib import Path

from app.config import settings
from app.schemas.attachment import AttachmentMetadata

class FileService:
    """Service for handling file uploads and storage"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.attachments_dir = self.upload_dir / "attachments"
        self.temp_dir = self.upload_dir / "temp"
        
        self.attachments_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # In-memory storage for file metadata (in production, use database)
        self._file_metadata: Dict[str, AttachmentMetadata] = {}
    
    def save_file(self, file_content: BinaryIO, filename: str, content_type: str) -> AttachmentMetadata:
        """
        Save uploaded file and return metadata
        """
        # Generate unique file ID
        file_id = str(uuid4())
        
        # Generate safe filename
        file_extension = Path(filename).suffix
        stored_filename = f"{file_id}{file_extension}"
        file_path = self.attachments_dir / stored_filename
        
        # Determine content type if not provided
        if not content_type or content_type == "application/octet-stream":
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_content, buffer)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Create metadata
        metadata = AttachmentMetadata(
            file_id=file_id,
            original_filename=filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_size=file_size,
            content_type=content_type,
            upload_timestamp=datetime.utcnow(),
            is_temporary=True
        )
        
        # Store metadata
        self._file_metadata[file_id] = metadata
        
        return metadata
    
    def get_file_metadata(self, file_id: str) -> Optional[AttachmentMetadata]:
        """Get file metadata by ID"""
        return self._file_metadata.get(file_id)
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """Get file content by ID"""
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            return None
        
        try:
            with open(metadata.file_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file and metadata"""
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            return False
        
        try:
            # Delete physical file
            Path(metadata.file_path).unlink(missing_ok=True)
            
            # Remove metadata
            del self._file_metadata[file_id]
            
            return True
        except Exception:
            return False
    
    def cleanup_temporary_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than max_age_hours"""
        deleted_count = 0
        current_time = datetime.utcnow()
        
        # Get list of file IDs to avoid modifying dict during iteration
        file_ids = list(self._file_metadata.keys())
        
        for file_id in file_ids:
            metadata = self._file_metadata[file_id]
            if metadata.is_temporary:
                age_hours = (current_time - metadata.upload_timestamp).total_seconds() / 3600
                if age_hours > max_age_hours:
                    if self.delete_file(file_id):
                        deleted_count += 1
        
        return deleted_count
    
    def validate_file(self, filename: str, content_type: str, file_size: int) -> Optional[str]:
        """
        Validate file upload requirements
        Returns error message if validation fails, None if valid
        """
        # Check file size
        if file_size > settings.max_file_size:
            return f"File size ({file_size} bytes) exceeds maximum allowed size ({settings.max_file_size} bytes)"
        
        # Check file type for images
        if content_type.startswith("image/"):
            if file_size > settings.max_image_size:
                return f"Image size ({file_size} bytes) exceeds maximum allowed size ({settings.max_image_size} bytes)"
            
            if content_type not in settings.allowed_image_types:
                return f"Image type {content_type} is not allowed"
        
        # Check file type for documents
        if content_type == "application/pdf":
            if file_size > settings.max_pdf_size:
                return f"PDF size ({file_size} bytes) exceeds maximum allowed size ({settings.max_pdf_size} bytes)"
        
        if content_type in settings.allowed_document_types:
            # Document type is allowed
            pass
        elif content_type in settings.allowed_image_types:
            # Image type is allowed
            pass
        else:
            return f"File type {content_type} is not allowed"
        
        return None
