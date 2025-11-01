# src/alerts.py
"""
Simple email alerts using SMTP. Configure with environment variables:
MDM_SMTP_HOST, MDM_SMTP_PORT, MDM_SMTP_USER, MDM_SMTP_PASS, MDM_ALERT_TO (comma-separated)
"""
import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get("MDM_SMTP_HOST")
SMTP_PORT = int(os.environ.get("MDM_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("MDM_SMTP_USER")
SMTP_PASS = os.environ.get("MDM_SMTP_PASS")
ALERT_TO = os.environ.get("MDM_ALERT_TO", "")

def send_email_if_needed(subject: str, body: str, attachment_path: str = None):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and ALERT_TO):
        print("SMTP not configured or MDM_ALERT_TO empty; skipping email.")
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO.split(",")
    msg.set_content(body)
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            data = f.read()
        msg.add_attachment(data, maintype="text", subtype="csv", filename=os.path.basename(attachment_path))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    print("Alert email sent to:", ALERT_TO)
