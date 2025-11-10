from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import base64


class InputValues(BaseModel):
    """Схема на вход определения ям"""
    user_id: Optional[str] = Field(None, max_length=50)
    latitude: str = Field(..., min_length=1, max_length=50, description="Широта")
    longitude: str = Field(..., min_length=1, max_length=50, description="Долгота")

    class Config:
        from_attributes = True


class ImageBase64Input(BaseModel):
    """Входные данные с изображением в base64"""
    image_base64: str = Field(..., description="Изображение в формате base64")
    user_id: Optional[str] = Field(None, max_length=50)
    latitude: str = Field(..., min_length=1, max_length=50, description="Широта")
    longitude: str = Field(..., min_length=1, max_length=50, description="Долгота")
    filename: Optional[str] = Field(None, description="Название файла (опционально)")

    @validator('image_base64')
    def validate_base64(cls, v):
        """Проверка корректности base64 строки"""
        try:
            if ',' in v:
                v = v.split(',', 1)[1]
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError("Некорректная base64 строка")


class MultipleImagesBase64Input(BaseModel):
    """Входные данные с несколькими изображениями в base64"""
    images_base64: List[str] = Field(..., description="Список изображений в base64", max_items=10)
    user_id: Optional[str] = Field(None, max_length=50)
    latitude: str = Field(..., min_length=1, max_length=50, description="Широта")
    longitude: str = Field(..., min_length=1, max_length=50, description="Долгота")
    filenames: Optional[List[str]] = Field(None, description="Названия файлов (опционально)")


class VideoBase64Input(BaseModel):
    """Входные данные с видео в base64"""
    video_base64: str = Field(..., description="Видео в формате base64")
    user_id: Optional[str] = Field(None, max_length=50)
    latitude: str = Field(..., min_length=1, max_length=50, description="Широта")
    longitude: str = Field(..., min_length=1, max_length=50, description="Долгота")
    filename: Optional[str] = Field(None, description="Название файла (опционально)")


# ============== МОДЕЛИ ОТВЕТОВ ==============

class SeverityStats(BaseModel):
    """Статистика по уровням опасности"""
    CRITICAL: int = 0
    HIGH: int = 0
    MEDIUM: int = 0
    LOW: int = 0


class DetectionResponse(BaseModel):
    """Ответ при обработке одного изображения"""
    user_id: str
    filename: str
    detections: SeverityStats
    average_risk: float
    max_risk: float
    total_potholes: int
    image_url: str
    address: Optional[str] = Field(None, description="Адрес (если удалось определить)")
    latitude: str
    longitude: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class SingleImageResult(BaseModel):
    """Результат обработки одного изображения в батче"""
    filename: str
    index: int
    detections: SeverityStats
    average_risk: float
    max_risk: float
    total_potholes: int
    image_url: Optional[str] = None
    error: Optional[str] = None


class MultipleDetectionResponse(BaseModel):
    """Ответ при обработке нескольких изображений"""
    user_id: str
    total_images: int
    successful: int
    failed: int
    results: List[SingleImageResult]
    address: Optional[str] = Field(None, description="Адрес (если удалось определить)")
    latitude: str
    longitude: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class VideoDetectionResponse(BaseModel):
    """Ответ при обработке видео"""
    filename: str
    total_frames: int
    processed_frames: int
    detections: SeverityStats
    average_risk: float
    max_risk: float
    duration_seconds: float
    video_url: str
    address: Optional[str] = Field(None, description="Адрес (если удалось определить)")
    latitude: str
    longitude: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)
