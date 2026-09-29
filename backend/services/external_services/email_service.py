"""
Email Service для отправки заявлений через Яндекс Почту.
"""

import logging
import mimetypes
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
from typing import Optional, List

from backend.core.config import configs

logger = logging.getLogger(__name__)


class EmailService:
    """Отправка заявлений через SMTP Яндекса."""

    def __init__(self):
        self.smtp_host = configs.YANDEX_SMTP_HOST
        self.smtp_port = configs.YANDEX_SMTP_PORT
        self.smtp_user = configs.YANDEX_SMTP_USER
        self.smtp_password = configs.YANDEX_SMTP_PASSWORD
        self.from_name = configs.EMAIL_FROM_NAME

    @property
    def is_configured(self) -> bool:
        return bool(self.smtp_user and self.smtp_password)

    def send_complaint_email(
            self,
            to_email: str,
            subject: str,
            body_text: str,
            attachments: Optional[List[tuple]] = None
    ) -> bool:
        if not self.is_configured:
            logger.error("Яндекс SMTP не настроен: заполните YANDEX_SMTP_USER и YANDEX_SMTP_PASSWORD")
            return False
        if not to_email:
            logger.error("Не указан email получателя заявления")
            return False

        message = EmailMessage()
        message["From"] = formataddr((self.from_name, self.smtp_user))
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body_text, subtype="plain", charset="utf-8")

        for filename, file_data in attachments or []:
            mime_type, _ = mimetypes.guess_type(filename)
            main_type, sub_type = (mime_type or "application/octet-stream").split("/", 1)
            message.add_attachment(
                file_data,
                maintype=main_type,
                subtype=sub_type,
                filename=filename
            )

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                    self.smtp_host,
                    self.smtp_port,
                    timeout=30,
                    context=context
            ) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            logger.info("Заявление отправлено через Яндекс SMTP получателю %s", to_email)
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("Яндекс отклонил авторизацию: используйте пароль приложения, а не пароль аккаунта")
        except smtplib.SMTPRecipientsRefused:
            logger.error("Яндекс отклонил адрес получателя %s", to_email)
        except smtplib.SMTPException as error:
            logger.error("Ошибка Яндекс SMTP: %s", error)
        except OSError as error:
            logger.error("Не удалось подключиться к Яндекс SMTP: %s", error)
        return False
