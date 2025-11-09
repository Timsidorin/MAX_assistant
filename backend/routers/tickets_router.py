from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import base64
from datetime import datetime
import uuid

from backend.core.database import get_async_session
from backend.schemas.cv_schema import (
    ImageBase64Input, MultipleImagesBase64Input, VideoBase64Input,
    DetectionResponse, MultipleDetectionResponse, VideoDetectionResponse
)
from backend.services.pothole_detection_service import PotholeDetectionService

tickets_router = APIRouter(prefix="/api/tickets", tags=["Заявки"])


@tickets_router.post("/create", summary="Создать заявку", response_model=DetectionResponse)
async def create_ticket(
):
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )
