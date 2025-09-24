from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class EmailSendRequest(BaseModel):
    recipients: List[EmailStr] = Field(..., description="List of recipient email addresses.")
    subject: str = Field(..., min_length=1, description="Subject of the email.")
    body: str = Field(..., min_length=1, description="Plain text body of the email.")
    sender_email: Optional[EmailStr] = Field(None, description="Optional sender email address. If not provided, uses default from settings.")
    sender_name: Optional[str] = Field(None, description="Optional sender name. If not provided, uses default from settings.")

    class Config:
        json_schema_extra = {
            "example": {
                "recipients": ["johnnyj@nvidia.com"],
                "subject": "Test Email from NotifyHubLite",
                "body": "Hello Johnny,\n\nThis is a plain text test email from NotifyHubLite API.",
                "sender_email": "noreply@203.18.50.4.nip.io",
                "sender_name": "NotifyHub System"
            }
        }


class EmailSendResponse(BaseModel):
    """Response schema for email send result"""
    
    success: bool = Field(..., description="Whether email was sent successfully")
    message: str = Field(..., description="Success or error message")
    email_id: Optional[str] = Field(None, description="Unique email ID if successful")
    recipients: Optional[int] = Field(None, description="Number of recipients")
    timestamp: datetime = Field(..., description="Send timestamp")
    error: Optional[str] = Field(None, description="Error details if failed")


class SMTPTestResponse(BaseModel):
    """Response schema for SMTP connection test"""
    
    success: bool = Field(..., description="Whether connection test passed")
    message: str = Field(..., description="Test result message")
    host: str = Field(..., description="SMTP host")
    port: int = Field(..., description="SMTP port")
    error: Optional[str] = Field(None, description="Error details if failed")
