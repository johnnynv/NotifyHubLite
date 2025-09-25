import logging
from typing import List, Optional, Dict, Any
from uuid import uuid4

from app.schemas.email import EmailSendRequest
from app.utils.smtp_client import SMTPClient

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_client = SMTPClient()

    async def send_plain_text_email(self, email_request: EmailSendRequest) -> dict:
        """
        Sends a plain text email based on the request.
        """
        email_id = str(uuid4())
        logger.info(f"[{email_id}] Sending email to {email_request.recipients}")

        try:
            await self.smtp_client.send_plain_email(
                recipients=email_request.recipients,
                subject=email_request.subject,
                body=email_request.body,
                sender_email=email_request.sender_email,
                sender_name=email_request.sender_name
            )
            logger.info(f"[{email_id}] Email sent successfully")
            return {
                "email_id": email_id,
                "status": "success",
                "message": "Plain text email sent successfully."
            }
        except Exception as e:
            logger.error(f"[{email_id}] Failed to send email: {e}")
            return {
                "email_id": email_id,
                "status": "failed",
                "message": f"Failed to send email: {e}"
            }
    
    def test_smtp_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection
        
        Returns:
            dict: Connection test result
        """
        return self.smtp_client.test_connection()
