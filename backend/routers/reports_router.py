# backend/routers/reports_router.py

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from typing import Optional, Annotated
import uuid

from backend.depends import ReportServiceDep
from backend.schemas.report_schema import (
    ReportCreateDraft, ReportUpdate,
    ReportDraftCreatedResponse, ReportResponse, ReportListResponse,
    ReportSubmitResponse, ReportStatusEnum, ReportPriorityEnum
)

report_router = APIRouter(prefix="/api/reports", tags=["Заявки"])


@report_router.post(
    "/draft",
    response_model=ReportDraftCreatedResponse,
    summary="Создать черновик заявки"
)
async def create_draft(
    payload: ReportCreateDraft,
    report_service: ReportServiceDep = None
):
    """Создание черновика заявки"""
    return await report_service.create_draft(payload)


@report_router.post(
    "/submit/{report_uuid}",
    response_model=ReportSubmitResponse,
    summary="Отправить заявку"
)
async def submit_report(
    report_uuid: uuid.UUID,
    background_tasks: BackgroundTasks,
    report_service: ReportServiceDep = None
):
    """
    Отправить заявку на обработку.
    Поисковый агент будет:
    1. Искать подходящий канал взаимодействия (email, форма, API)
    2. Формировать и отправлять заявку
    3. Отслеживать статус
    """
    return await report_service.submit_report(report_uuid, background_tasks)


@report_router.get(
    "/{report_uuid}",
    response_model=ReportResponse,
    summary="Получить заявку по UUID"
)
async def get_report(
    report_uuid: uuid.UUID,
    report_service: ReportServiceDep = None
):
    """Получение полной информации о заявке"""
    return await report_service.get_by_uuid(report_uuid)


@report_router.patch(
    "/draft/{report_uuid}",
    response_model=ReportResponse,
    summary="Обновить черновик"
)
async def update_draft(
    report_uuid: uuid.UUID,
    payload: ReportUpdate,
    report_service: ReportServiceDep = None
):
    """Обновление черновика заявки"""
    return await report_service.update_draft(report_uuid, payload)


@report_router.get(
    "/",
    response_model=ReportListResponse,
    summary="Получить список заявок"
)
async def list_reports(
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    status: Optional[ReportStatusEnum] = Query(None, description="Фильтр по статусу"),
    priority: Optional[ReportPriorityEnum] = Query(None, description="Фильтр по приоритету"),
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    report_service: ReportServiceDep = None
):
    """Получение списка заявок с фильтрацией и пагинацией"""
    return await report_service.get_list(
        user_id=user_id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit
    )


@report_router.delete(
    "/draft/{report_uuid}",
    summary="Удалить черновик"
)
async def delete_draft(
    report_uuid: uuid.UUID,
    report_service: ReportServiceDep = None
):
    """Удаление черновика заявки"""
    return await report_service.delete_draft(report_uuid)
