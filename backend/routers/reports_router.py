# reports_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from backend.core.database import get_async_session
from backend.services.report_service import ReportService
from backend.schemas.report_schema import (
    ReportCreateDraft, ReportUpdate,
    ReportDraftCreatedResponse, ReportResponse, ReportListResponse,
    ReportStatusEnum, ReportPriorityEnum
)

report_router = APIRouter(prefix="/api/reports", tags=["Заявки"])


@report_router.post(
    "/draft",
    response_model=ReportDraftCreatedResponse
)
async def create_draft(
        payload: ReportCreateDraft,
        db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    return await service.create_draft(payload)


@report_router.get(
    "/{report_uuid}",
    response_model=ReportResponse
)
async def get_report(
        report_uuid: uuid.UUID,
        db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    return await service.get_by_uuid(report_uuid)


@report_router.patch(
    "/draft/{report_uuid}",
    response_model=ReportResponse
)
async def update_draft(
        report_uuid: uuid.UUID,
        payload: ReportUpdate,
        db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    return await service.update_draft(report_uuid, payload)


@report_router.get(
    "/",
    response_model=ReportListResponse
)
async def list_reports(
        user_id: Optional[str] = Query(None),
        status: Optional[ReportStatusEnum] = Query(None),
        priority: Optional[ReportPriorityEnum] = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    return await service.get_list(
        user_id=user_id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit
    )


@report_router.delete(
    "/draft/{report_uuid}"
)
async def delete_draft(
        report_uuid: uuid.UUID,
        db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    return await service.delete_draft(report_uuid)