from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.email import EmailSendRequest
from app.services.email_service import EmailService
from app.config import settings

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
email_service = EmailService()

@router.post(
    "/send",
    summary="Send Email (Plain, HTML, or Multipart)",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)]
)
async def send_email_api(email_request: EmailSendRequest):
    """
    Sends an email to the specified recipients.
    
    Supports three email types:
    - plain: Plain text email (requires 'body')
    - html: HTML email (requires 'html_body')
    - multipart: Both plain text and HTML (requires both 'body' and 'html_body')
    
    Requires API key authentication.
    """
    try:
        result = await email_service.send_email(email_request)
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/send-plain",
    summary="Send Plain Text Email (Legacy)",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)]
)
async def send_plain_text_email_api(email_request: EmailSendRequest):
    """
    Sends a plain text email to the specified recipients.
    
    Legacy endpoint - use /send with email_type="plain" instead.
    Requires API key authentication.
    """
    try:
        result = await email_service.send_plain_text_email(email_request)
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
