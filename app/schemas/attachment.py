from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AttachmentUploadResponse(BaseModel):
    """Response schema for file upload result"""
    
    success: bool = Field(..., description="Whether file was uploaded successfully")
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME content type")
    upload_timestamp: datetime = Field(..., description="Upload timestamp")
    error: Optional[str] = Field(None, description="Error details if failed")

class AttachmentInfo(BaseModel):
    """Attachment information for email sending"""
    
    file_id: str = Field(..., description="File ID from upload response")
    attachment_type: str = Field(default="attachment", description="Type: attachment, inline_image")
    filename: Optional[str] = Field(None, description="Custom filename for attachment")
    content_id: Optional[str] = Field(None, description="Content-ID for inline images (cid:)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file_id": "uuid-123-456",
                    "attachment_type": "attachment",
                    "filename": "document.pdf"
                },
                {
                    "file_id": "uuid-789-012",
                    "attachment_type": "inline_image",
                    "content_id": "image1"
                }
            ]
        }
    }

class AttachmentMetadata(BaseModel):
    """Internal attachment metadata for storage"""
    
    file_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_timestamp: datetime
    is_temporary: bool = True  # Files are deleted after email is sent
