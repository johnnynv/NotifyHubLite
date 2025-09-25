from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from app.config import settings
from app.schemas.attachment import AttachmentUploadResponse
from app.services.file_service import FileService

# Security scheme for API key authentication
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify API key from Authorization header
    """
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return credentials

router = APIRouter()
file_service = FileService()

@router.post(
    "/upload",
    summary="Upload File for Email Attachment",
    response_model=AttachmentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)]
)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file that can be used as an email attachment.
    
    The uploaded file will be temporarily stored and can be referenced
    by its file_id when sending emails with attachments.
    
    Supported file types:
    - Images: JPEG, PNG, GIF, WebP (max 5MB)
    - Documents: PDF, DOC, DOCX (max 25MB total)
    
    Files are automatically deleted after 24 hours.
    """
    try:
        # Read file content to get size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer for later reading
        await file.seek(0)
        
        # Validate file
        validation_error = file_service.validate_file(
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size
        )
        
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error
            )
        
        # Save file
        metadata = file_service.save_file(
            file_content=file.file,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return AttachmentUploadResponse(
            success=True,
            file_id=metadata.file_id,
            filename=metadata.original_filename,
            file_size=metadata.file_size,
            content_type=metadata.content_type,
            upload_timestamp=metadata.upload_timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.delete(
    "/{file_id}",
    summary="Delete Uploaded File",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)]
)
async def delete_file(file_id: str):
    """
    Delete an uploaded file by its ID.
    """
    try:
        success = file_service.delete_file(file_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found"
            )
        
        return {
            "success": True,
            "message": f"File {file_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.post(
    "/cleanup",
    summary="Cleanup Temporary Files",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)]
)
async def cleanup_files():
    """
    Clean up temporary files older than 24 hours.
    """
    try:
        deleted_count = file_service.cleanup_temporary_files()
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} temporary files"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup files: {str(e)}"
        )
