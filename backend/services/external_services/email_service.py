# backend/services/email_service.py

"""
Email Service для отправки заявлений через Mail.ru.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from dotenv import load_dotenv

from backend.core.config import configs

load_dotenv()

MAILRU_SMTP_HOST = configs.MAILRU_SMTP_HOST
MAILRU_SMTP_PORT = configs.MAILRU_SMTP_PORT
MAILRU_SMTP_USER = configs.MAILRU_SMTP_USER
MAILRU_SMTP_PASSWORD = configs.MAILRU_SMTP_PASSWORD


class EmailService:
    """Сервис для отправки email через Mail.ru."""

    def __init__(self):
        self.smtp_host = MAILRU_SMTP_HOST
        self.smtp_port = MAILRU_SMTP_PORT
        self.smtp_user = MAILRU_SMTP_USER
        self.smtp_password = MAILRU_SMTP_PASSWORD

    def send_complaint_email(
            self,
            to_email: str,
            subject: str,
            body_text: str,
            attachments: Optional[List[tuple]] = None
    ) -> bool:
        """
        Отправляет email с заявлением через Mail.ru.
        Returns:
            bool: True если успешно отправлено
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_user
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body_text, "plain", "utf-8"))

            if attachments:
                for filename, file_data in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
                    message.attach(part)
                    print(f"[Email Service] Attached: {filename} ({len(file_data)} bytes)")

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            return True

        except smtplib.SMTPAuthenticationError as e:
            return False
        except Exception as e:
            return False


