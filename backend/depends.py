from backend.core.database import get_async_session
from backend.services.ai_agent_service import AIAgentService
from backend.services.document_service import DocumentService
from backend.services.external_services.email_service import EmailService
from backend.services.external_services.gigachat_service import GigaChatService
from backend.services.users_service import UserService




_email_service = None
_document_service = None
_gigachat_service = None

async def get_user_service() -> UserService:
    """Получение сервиса пользователя с сессией"""
    session = await get_async_session()
    return UserService(session)

def get_email_service() -> EmailService:
    """Получение сервиса для работы с email"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def get_document_service() -> DocumentService:
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service



def get_gigachat_service() -> GigaChatService:
    global _gigachat_service
    if _gigachat_service is None:
        _gigachat_service = GigaChatService()
    return _gigachat_service


def get_service():
    """Singleton для AIAgentService."""
    global _service
    if _service is None:
        _service = AIAgentService()
    return _service

