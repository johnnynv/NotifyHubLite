#!/usr/bin/env python3
"""
Final SMTP Test with NVIDIA Mail Relay
"""
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def test_nvidia_smtp():
    smtp_server = 'localhost'
    smtp_port = 25
    from_email = 'johnnyj@nvidia.com'  # Using NVIDIA email as sender
    to_email = 'johnnyj@nvidia.com'
    
    subject = f'NotifyHubLite SMTP Test via NVIDIA Relay - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    body = f"""Hello Johnny,

This is a test email from NotifyHubLite using NVIDIA's mail relay!

Server Details:
- Local SMTP: {smtp_server}:{smtp_port}
- Relay: mail.nvidia.com:587
- From: {from_email}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- System: Postfix + NVIDIA Relay

This email should successfully reach your inbox!

Best regards,
NotifyHubLite System
"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        print(f"Connecting to local SMTP server {smtp_server}:{smtp_port}...")
        print("(Will relay through mail.nvidia.com:587)")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(0)  # Disable debug to avoid clutter
        
        print("Sending email...")
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        
        print("SUCCESS: Email sent to relay server!")
        print(f"Recipient: {to_email}")
        print(f"Subject: {subject}")
        print("\nNOTE: Check docker logs for relay status:")
        print("docker logs smtp-server | tail -10")
        return True
        
    except Exception as e:
        print(f"ERROR: Email sending failed: {e}")
        return False

if __name__ == "__main__":
    test_nvidia_smtp()
