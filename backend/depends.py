from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_session
from backend.services.ai_agent_service import AIAgentService
from backend.services.document_service import DocumentService
from backend.services.external_services.email_service import EmailService
from backend.services.external_services.gigachat_service import GigaChatService
from backend.services.users_service import UserService
from backend.services.report_service import ReportService


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_user_service(
    session: AsyncSessionDep
) -> UserService:
    """Dependency для получения UserService с автоматическим управлением сессией"""
    return UserService(session)


async def get_report_service(
    session: AsyncSessionDep
) -> ReportService:
    """Dependency для получения ReportService с автоматическим управлением сессией"""
    return ReportService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]


# ===== Singleton Services (без DB) =====
_email_service = None
_document_service = None
_gigachat_service = None
_ai_agent_service = None


def get_email_service() -> EmailService:
    """Singleton: Получение сервиса для работы с email"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


def get_document_service() -> DocumentService:
    """Singleton: Получение сервиса для работы с документами"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service


def get_gigachat_service() -> GigaChatService:
    """Singleton: Получение сервиса GigaChat"""
    global _gigachat_service
    if _gigachat_service is None:
        _gigachat_service = GigaChatService()
    return _gigachat_service


def get_ai_agent_service() -> AIAgentService:
    """Singleton: Получение AI Agent сервиса"""
    global _ai_agent_service
    if _ai_agent_service is None:
        _ai_agent_service = AIAgentService()
    return _ai_agent_service


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
GigaChatServiceDep = Annotated[GigaChatService, Depends(get_gigachat_service)]
AIAgentServiceDep = Annotated[AIAgentService, Depends(get_ai_agent_service)]
