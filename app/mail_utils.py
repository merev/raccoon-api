import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeSerializer

serializer = URLSafeSerializer(os.getenv("EMAIL_SECRET", "change-me"))

def generate_decline_token(reservation_id: str) -> str:
    return serializer.dumps(reservation_id)

def verify_decline_token(token: str) -> str:
    return serializer.loads(token)

def send_reservation_email(to_email: str, reservation_data: dict):
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    sender = os.getenv("SMTP_SENDER", "no-reply@raccoon.bg")

    reservation_id = reservation_data["reservation_id"]
    token = generate_decline_token(reservation_id)
    decline_url = f"https://staging.raccoon.bg/api/reservations/decline?token={token}"

    html = f"""
    <html>
      <body>
        <h3>Благодарим Ви за заявката!</h3>
        <p>Тип апартамент: {reservation_data['flat_type']}</p>
        <p>План: {reservation_data.get('plan', 'Потребителски')}</p>
        <p>Обща цена: {reservation_data['total_price']} лв</p>
        <br>
        <a href="{decline_url}" style="padding: 10px 20px; background: #e00; color: white; text-decoration: none;">Откажи заявката</a>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Заявка за почистване - Raccoon Cleaning"
    msg["From"] = sender
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.sendmail(sender, to_email, msg.as_string())