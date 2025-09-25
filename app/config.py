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
    app_version: str = "1.2.0"
    api_key: str = "notify-hub-api-key-123"  # Default for development. Use env var NOTIFYHUB_API_KEY in production
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Network Configuration
    server_ip: str = "10.78.14.61"  # Server public IP address
    domain_suffix: str = "nip.io"   # Domain suffix for development
    
    # Database Configuration  
    database_url: str = "postgresql://notifyhub:secure-password-123@localhost:5432/notifyhublite"
    
    # SMTP Configuration (connecting to our Postfix relay)
    smtp_host: str = "localhost"
    smtp_port: int = 25
    smtp_username: str = ""  # No auth needed for local relay
    smtp_password: str = ""  # No auth needed for local relay
    smtp_use_tls: bool = False
    smtp_from_name: str = "NotifyHub System"
    smtp_from_email: str = ""  # Will be set dynamically based on server_ip and domain_suffix
    
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

    @property
    def base_domain(self) -> str:
        """Generate base domain from IP and suffix"""
        return f"{self.server_ip}.{self.domain_suffix}"
    
    @property
    def mail_hostname(self) -> str:
        """Generate mail server hostname"""
        return f"mail.{self.base_domain}"
    
    @property
    def default_from_email(self) -> str:
        """Generate default from email address"""
        return f"noreply@{self.base_domain}"


# Global settings instance
settings = Settings()

# Set dynamic email if not provided
if not settings.smtp_from_email:
    settings.smtp_from_email = settings.default_from_email
