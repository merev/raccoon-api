from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

router = APIRouter()

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/contact")
async def contact_form(message: ContactMessage):
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    smtp_user = os.getenv("SMTP_USERNAME")  # raccoon.assistant@gmail.com
    smtp_pass = os.getenv("SMTP_PASSWORD")
    sender = smtp_user  # must be raccoon.assistant@gmail.com
    receiver = "kmerev.raccoon@gmail.com"  # receiving email

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Ново запитване от сайта"
    msg["From"] = sender
    msg["To"] = receiver

    html = f"""
    <html>
      <body>
        <h4>Ново съобщение от контактната форма</h4>
        <p><strong>Име:</strong> {message.name}</p>
        <p><strong>Email за връзка:</strong> {message.email}</p>
        <p><strong>Съобщение:</strong></p>
        <p>{message.message}</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(sender, receiver, msg.as_string())
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
