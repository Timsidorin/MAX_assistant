# backend/routers/cv_router.py

from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import base64
from datetime import datetime
import uuid

from backend.depends import AsyncSessionDep
from backend.schemas.cv_schema import (
    ImageBase64Input, MultipleImagesBase64Input, VideoBase64Input,
    DetectionResponse, MultipleDetectionResponse, VideoDetectionResponse
)
from backend.services.pothole_detection_service import PotholeDetectionService

cv_router = APIRouter(prefix="/api/detect", tags=["Анализ дорожного покрытия"])


@lru_cache()
def get_pothole_detection_service():
    """Singleton для PotholeDetectionService"""
    return PotholeDetectionService()


# Создаём Annotated тип для удобства
PotholeServiceDep = Annotated[PotholeDetectionService, Depends(get_pothole_detection_service)]


@cv_router.post("/image", summary="Обработка одного изображения", response_model=DetectionResponse)
async def detect_single_image(
    payload: ImageBase64Input,
    db: AsyncSessionDep,
    service: PotholeServiceDep
):
    try:
        image_base64 = payload.image_base64
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]

        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка декодирования base64: {str(e)}"
            )

        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Размер изображения превышает 10 MB"
            )

        if not payload.filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"pothole_{timestamp}_{unique_id}.jpg"
        else:
            filename = payload.filename

        result = await service.process_single_image(
            image_bytes=image_bytes,
            input_data=payload,
            filename=filename,
            db=db
        )

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )


@cv_router.post("/images", summary="Обработка нескольких изображений", response_model=MultipleDetectionResponse)
async def detect_multiple_images(
    payload: MultipleImagesBase64Input,
    db: AsyncSessionDep,
    service: PotholeServiceDep
):
    try:
        if not payload.images_base64:
            raise HTTPException(status_code=400, detail="Не передано ни одного изображения")

        if len(payload.images_base64) > 10:
            raise HTTPException(status_code=400, detail="Максимум 10 изображений")

        decoded_images = []
        for idx, img_base64 in enumerate(payload.images_base64):
            try:
                if ',' in img_base64:
                    img_base64 = img_base64.split(',', 1)[1]

                image_bytes = base64.b64decode(img_base64)

                if payload.filenames and idx < len(payload.filenames):
                    filename = payload.filenames[idx]
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"pothole_{timestamp}_{unique_id}_{idx}.jpg"

                decoded_images.append((image_bytes, filename))

            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ошибка декодирования изображения {idx + 1}: {str(e)}"
                )

        result = await service.process_multiple_images_bytes(
            images_data=decoded_images,
            input_data=payload,
            db=db
        )

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@cv_router.post("/video", summary="Обработка видео", response_model=VideoDetectionResponse)
async def detect_video(
    payload: VideoBase64Input,
    db: AsyncSessionDep,
    service: PotholeServiceDep
):
    try:
        video_base64 = payload.video_base64
        if ',' in video_base64:
            video_base64 = video_base64.split(',', 1)[1]

        try:
            video_bytes = base64.b64decode(video_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка декодирования base64: {str(e)}"
            )

        if len(video_bytes) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Размер видео превышает 100 MB"
            )

        if not payload.filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"pothole_video_{timestamp}_{unique_id}.mp4"
        else:
            filename = payload.filename

        result = await service.process_video_bytes(
            video_bytes=video_bytes,
            input_data=payload,
            filename=filename,
            db=db
        )

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
