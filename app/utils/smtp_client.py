import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class SMTPClient:
    def __init__(self):
        self.smtp_server = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.smtp_from_name = settings.smtp_from_name
        self.smtp_from_email = settings.smtp_from_email

    async def send_plain_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> str:
        """
        Sends a plain text email.
        """
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
        msg["To"] = ", ".join(recipients)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            logger.info(f"Plain text email sent successfully to {recipients}")
            return "Email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send plain text email: {e}")
            raise

    # TODO: Add send_html_email, send_email_with_attachments, etc.
    
    def test_connection(self) -> dict:
        """
        Test SMTP connection
        
        Returns:
            dict: Connection test result
        """
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                return {
                    "success": True,
                    "message": "SMTP connection successful",
                    "host": self.host,
                    "port": self.port
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "host": self.host,
                "port": self.port
            }
