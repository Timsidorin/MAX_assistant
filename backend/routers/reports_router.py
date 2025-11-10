from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from backend.core.database import get_async_session
from backend.services.report_service import ReportService
from backend.schemas.report_schema import (
    ReportCreate, ReportUpdate, ReportAddMedia, ReportStatusUpdate,
    ReportResponse, ReportListResponse, ReportDeleteResponse,
    ReportStatusEnum, ReportPriorityEnum
)

report_router = APIRouter(prefix="/api/reports", tags=["Заявки"])


@report_router.post("/draft", response_model=ReportResponse, summary="Создать черновик")
async def create_draft(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Создание черновика заявки"""
    service = ReportService(db)
    return await service.create_draft(payload)


@report_router.get("/{report_uuid}", response_model=ReportResponse, summary="Получить заявку")
async def get_report(
    report_uuid: uuid.UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Получение заявки по UUID"""
    service = ReportService(db)
    return await service.get_by_uuid(report_uuid)


@report_router.patch("/draft/{report_uuid}", response_model=ReportResponse, summary="Обновить черновик")
async def update_draft(
    report_uuid: uuid.UUID,
    payload: ReportUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление черновика"""
    service = ReportService(db)
    return await service.update_draft(report_uuid, payload)


@report_router.post("/draft/{report_uuid}/add-media", response_model=ReportResponse, summary="Добавить медиа")
async def add_media(
    report_uuid: uuid.UUID,
    payload: ReportAddMedia,
    db: AsyncSession = Depends(get_async_session)
):
    """Добавление медиафайлов к черновику"""
    service = ReportService(db)
    return await service.add_media(report_uuid, payload)


@report_router.post("/draft/{report_uuid}/submit", response_model=ReportResponse, summary="Отправить заявку")
async def submit_report(
    report_uuid: uuid.UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Отправка заявки на рассмотрение"""
    service = ReportService(db)
    return await service.submit_report(report_uuid)


@report_router.get("/", response_model=ReportListResponse, summary="Список заявок")
async def list_reports(
    user_id: Optional[str] = Query(None),
    status: Optional[ReportStatusEnum] = Query(None),
    priority: Optional[ReportPriorityEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    """Список заявок с фильтрацией"""
    service = ReportService(db)
    return await service.get_list(
        user_id=user_id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit
    )


@report_router.delete("/draft/{report_uuid}", response_model=ReportDeleteResponse, summary="Удалить черновик")
async def delete_draft(
    report_uuid: uuid.UUID,
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление черновика"""
    service = ReportService(db)
    return await service.delete_draft(report_uuid)


@report_router.patch("/{report_uuid}/status", response_model=ReportResponse, summary="Обновить статус")
async def update_status(
    report_uuid: uuid.UUID,
    payload: ReportStatusUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление статуса заявки (для администратора)"""
    service = ReportService(db)
    return await service.update_status(report_uuid, payload)


@report_router.get("/drafts/list", response_model=list, summary="Черновики пользователя")
async def get_drafts(
    user_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить все черновики"""
    service = ReportService(db)
    return await service.get_drafts(user_id)


@report_router.get("/statistics/summary", summary="Статистика по заявкам")
async def get_statistics(
    user_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """Статистика по заявкам пользователя"""
    service = ReportService(db)
    return await service.get_statistics(user_id)
