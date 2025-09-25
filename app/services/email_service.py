import logging
from typing import List, Optional, Dict, Any
from uuid import uuid4

from app.schemas.email import EmailSendRequest
from app.utils.smtp_client import SMTPClient

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_client = SMTPClient()

    async def send_email(self, email_request: EmailSendRequest) -> dict:
        """
        Sends an email based on the request type (plain, html, or multipart).
        """
        email_id = str(uuid4())
        logger.info(f"[{email_id}] Sending {email_request.email_type} email to {email_request.recipients}")

        try:
            if email_request.email_type == "plain":
                await self.smtp_client.send_plain_email(
                    recipients=email_request.recipients,
                    subject=email_request.subject,
                    body=email_request.body,
                    sender_email=email_request.sender_email,
                    sender_name=email_request.sender_name,
                    cc=email_request.cc,
                    bcc=email_request.bcc
                )
                message = "Plain text email sent successfully."
            
            elif email_request.email_type == "html":
                await self.smtp_client.send_html_email(
                    recipients=email_request.recipients,
                    subject=email_request.subject,
                    html_body=email_request.html_body,
                    sender_email=email_request.sender_email,
                    sender_name=email_request.sender_name,
                    cc=email_request.cc,
                    bcc=email_request.bcc
                )
                message = "HTML email sent successfully."
            
            elif email_request.email_type == "multipart":
                await self.smtp_client.send_multipart_email(
                    recipients=email_request.recipients,
                    subject=email_request.subject,
                    text_body=email_request.body,
                    html_body=email_request.html_body,
                    sender_email=email_request.sender_email,
                    sender_name=email_request.sender_name,
                    cc=email_request.cc,
                    bcc=email_request.bcc
                )
                message = "Multipart email sent successfully."
            
            else:
                raise ValueError(f"Unsupported email type: {email_request.email_type}")

            logger.info(f"[{email_id}] Email sent successfully")
            return {
                "email_id": email_id,
                "status": "success",
                "message": message
            }
        except Exception as e:
            logger.error(f"[{email_id}] Failed to send email: {e}")
            return {
                "email_id": email_id,
                "status": "failed",
                "message": f"Failed to send email: {e}"
            }

    async def send_plain_text_email(self, email_request: EmailSendRequest) -> dict:
        """
        Legacy method for backward compatibility.
        Sends a plain text email based on the request.
        """
        # Set email type to plain and use the unified send_email method
        email_request.email_type = "plain"
        return await self.send_email(email_request)
    
    def test_smtp_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection
        
        Returns:
            dict: Connection test result
        """
        return self.smtp_client.test_connection()
