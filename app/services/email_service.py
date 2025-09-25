import logging
from typing import List, Optional, Dict, Any
from uuid import uuid4

from app.schemas.email import EmailSendRequest
from app.utils.smtp_client import SMTPClient
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_client = SMTPClient()
        self.file_service = FileService()

    async def send_email(self, email_request: EmailSendRequest) -> dict:
        """
        Sends an email based on the request type (plain, html, or multipart).
        Supports attachments if provided.
        """
        email_id = str(uuid4())
        logger.info(f"[{email_id}] Sending {email_request.email_type} email to {email_request.recipients}")

        try:
            # Process attachments if provided
            processed_attachments = None
            if email_request.attachments:
                processed_attachments = await self._process_attachments(email_request.attachments, email_id)
            
            # Send email with or without attachments
            if processed_attachments:
                # Use the attachment-capable method
                await self.smtp_client.send_email_with_attachments(
                    recipients=email_request.recipients,
                    subject=email_request.subject,
                    body=email_request.body,
                    html_body=email_request.html_body,
                    attachments=processed_attachments,
                    sender_email=email_request.sender_email,
                    sender_name=email_request.sender_name,
                    cc=email_request.cc,
                    bcc=email_request.bcc
                )
                attachment_count = len(processed_attachments)
                message = f"Email with {attachment_count} attachments sent successfully."
            else:
                # Use the original methods for emails without attachments
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

            # Clean up temporary attachments after sending
            if processed_attachments:
                await self._cleanup_attachments(email_request.attachments, email_id)

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

    async def _process_attachments(self, attachments: list, email_id: str) -> List[Dict[str, Any]]:
        """
        Process attachment list and prepare them for email sending
        """
        processed = []
        
        for attachment in attachments:
            # Get file metadata
            metadata = self.file_service.get_file_metadata(attachment.file_id)
            if not metadata:
                logger.warning(f"[{email_id}] Attachment file {attachment.file_id} not found")
                continue
            
            # Get file content
            content = self.file_service.get_file_content(attachment.file_id)
            if not content:
                logger.warning(f"[{email_id}] Could not read attachment file {attachment.file_id}")
                continue
            
            # Determine filename
            filename = attachment.filename or metadata.original_filename
            
            processed.append({
                'content': content,
                'filename': filename,
                'content_type': metadata.content_type,
                'content_id': attachment.content_id
            })
            
            logger.info(f"[{email_id}] Processed attachment: {filename} ({len(content)} bytes)")
        
        return processed

    async def _cleanup_attachments(self, attachments: list, email_id: str):
        """
        Clean up temporary attachment files after email is sent
        """
        for attachment in attachments:
            try:
                self.file_service.delete_file(attachment.file_id)
                logger.info(f"[{email_id}] Cleaned up attachment file {attachment.file_id}")
            except Exception as e:
                logger.warning(f"[{email_id}] Failed to cleanup attachment {attachment.file_id}: {e}")

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
