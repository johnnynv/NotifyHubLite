from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from .attachment import AttachmentInfo

class EmailSendRequest(BaseModel):
    recipients: List[EmailStr] = Field(..., description="List of recipient email addresses.")
    cc: Optional[List[EmailStr]] = Field(None, description="List of CC recipient email addresses.")
    bcc: Optional[List[EmailStr]] = Field(None, description="List of BCC recipient email addresses.")
    subject: str = Field(..., min_length=1, description="Subject of the email.")
    body: Optional[str] = Field(None, description="Plain text body of the email.")
    html_body: Optional[str] = Field(None, description="HTML body of the email.")
    email_type: str = Field(default="plain", description="Email type: plain, html, or multipart")
    attachments: Optional[List[AttachmentInfo]] = Field(None, description="List of file attachments")
    sender_email: Optional[EmailStr] = Field(None, description="Optional sender email address. If not provided, uses default from settings.")
    sender_name: Optional[str] = Field(None, description="Optional sender name. If not provided, uses default from settings.")

    @validator('email_type')
    def validate_email_type(cls, v):
        if v not in ['plain', 'html', 'multipart']:
            raise ValueError('email_type must be one of: plain, html, multipart')
        return v

    @validator('email_type', always=True)
    def validate_content_requirements(cls, v, values):
        body = values.get('body')
        html_body = values.get('html_body')
        
        if v == 'plain' and not body:
            raise ValueError('body is required for plain text emails')
        elif v == 'html' and not html_body:
            raise ValueError('html_body is required for HTML emails')
        elif v == 'multipart' and not (body and html_body):
            raise ValueError('Both body and html_body are required for multipart emails')
        
        return v


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
