import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders
from typing import List, Optional, Dict, Any
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
        sender_name: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """
        Sends a plain text email.
        """
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
        msg["To"] = ", ".join(recipients)
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        # Combine all recipients for sending
        all_recipients = recipients[:]
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, to_addrs=all_recipients)
            logger.info(f"Plain text email sent successfully to {all_recipients}")
            return "Email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send plain text email: {e}")
            raise

    async def send_html_email(
        self,
        recipients: List[str],
        subject: str,
        html_body: str,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """
        Sends an HTML email.
        """
        msg = MIMEText(html_body, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
        msg["To"] = ", ".join(recipients)
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        # Combine all recipients for sending
        all_recipients = recipients[:]
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, to_addrs=all_recipients)
            logger.info(f"HTML email sent successfully to {all_recipients}")
            return "HTML email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send HTML email: {e}")
            raise

    async def send_multipart_email(
        self,
        recipients: List[str],
        subject: str,
        text_body: str,
        html_body: str,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """
        Sends a multipart email with both plain text and HTML versions.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
        msg["To"] = ", ".join(recipients)
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        # Create the plain text and HTML parts
        text_part = MIMEText(text_body, "plain", "utf-8")
        html_part = MIMEText(html_body, "html", "utf-8")

        # Add parts to message (order matters: plain text first, then HTML)
        msg.attach(text_part)
        msg.attach(html_part)

        # Combine all recipients for sending
        all_recipients = recipients[:]
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, to_addrs=all_recipients)
            logger.info(f"Multipart email sent successfully to {all_recipients}")
            return "Multipart email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send multipart email: {e}")
            raise

    def _create_attachment(self, file_content: bytes, filename: str, content_type: str, content_id: Optional[str] = None) -> MIMEBase:
        """
        Create a MIME attachment from file content
        """
        if content_type.startswith('image/'):
            # Use MIMEImage for images
            attachment = MIMEImage(file_content)
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        elif content_type == 'application/pdf' or content_type.startswith('application/'):
            # Use MIMEApplication for PDFs and other applications
            attachment = MIMEApplication(file_content, _subtype=content_type.split('/')[-1])
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        else:
            # Use MIMEBase for other file types
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file_content)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        
        # Set Content-ID for inline images
        if content_id:
            attachment.add_header('Content-ID', f'<{content_id}>')
        
        return attachment

    async def send_email_with_attachments(
        self,
        recipients: List[str],
        subject: str,
        body: Optional[str] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """
        Send email with attachments.
        
        attachments format: [
            {
                'content': bytes,
                'filename': str,
                'content_type': str,
                'content_id': Optional[str]  # For inline images
            }
        ]
        """
        # Create the root message container
        if html_body and attachments and any(att.get('content_id') for att in attachments):
            # Use multipart/related for HTML with inline images
            msg = MIMEMultipart('related')
        else:
            # Use multipart/mixed for regular attachments
            msg = MIMEMultipart('mixed')
        
        msg["Subject"] = subject
        msg["From"] = f"{sender_name or self.smtp_from_name} <{sender_email or self.smtp_from_email}>"
        msg["To"] = ", ".join(recipients)
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        # Create text/html content container
        if body and html_body:
            # Both plain text and HTML
            text_container = MIMEMultipart('alternative')
            text_container.attach(MIMEText(body, 'plain', 'utf-8'))
            text_container.attach(MIMEText(html_body, 'html', 'utf-8'))
            msg.attach(text_container)
        elif html_body:
            # HTML only
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        elif body:
            # Plain text only
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Add attachments
        if attachments:
            for attachment in attachments:
                mime_attachment = self._create_attachment(
                    file_content=attachment['content'],
                    filename=attachment['filename'],
                    content_type=attachment['content_type'],
                    content_id=attachment.get('content_id')
                )
                msg.attach(mime_attachment)

        # Combine all recipients for sending
        all_recipients = recipients[:]
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, to_addrs=all_recipients)
            
            attachment_count = len(attachments) if attachments else 0
            logger.info(f"Email with {attachment_count} attachments sent successfully to {all_recipients}")
            return f"Email with {attachment_count} attachments sent successfully"
        except Exception as e:
            logger.error(f"Failed to send email with attachments: {e}")
            raise
    
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
