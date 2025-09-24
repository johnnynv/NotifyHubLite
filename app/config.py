"""
NotifyHubLite Configuration Management
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application Settings
    app_name: str = "NotifyHubLite API"
    app_version: str = "1.0.0"
    api_key: str = "notify-hub-api-key-123"  # Default for development. Use env var NOTIFYHUB_API_KEY in production
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Database Configuration  
    database_url: str = "postgresql://notifyhub:secure-password-123@localhost:5432/notifyhublite"
    
    # SMTP Configuration (connecting to our Postfix relay)
    smtp_host: str = "localhost"
    smtp_port: int = 25
    smtp_username: str = ""  # No auth needed for local relay
    smtp_password: str = ""  # No auth needed for local relay
    smtp_use_tls: bool = False
    smtp_from_name: str = "NotifyHub System"
    smtp_from_email: str = "noreply@203.18.50.4.nip.io"
    
    # File Storage Configuration
    upload_dir: str = "./uploads"
    max_file_size: int = 26214400  # 25MB
    max_image_size: int = 5242880  # 5MB
    max_pdf_size: int = 20971520   # 20MB
    
    # PDF Processing Configuration
    pdf_preview_pages_default: int = 3
    pdf_preview_pages_max: int = 10
    pdf_preview_dpi: int = 150
    
    # Security Configuration
    allowed_image_types: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp"
    ]
    allowed_document_types: List[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_prefix = "NOTIFYHUB_"  # Environment variables should start with NOTIFYHUB_
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from environment


# Global settings instance
settings = Settings()
