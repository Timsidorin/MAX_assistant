from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import uuid


class ReportStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReportPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SeverityStats(BaseModel):
    CRITICAL: int = 0
    HIGH: int = 0
    MEDIUM: int = 0
    LOW: int = 0


class ReportCreateDraft(BaseModel):
    user_id: Optional[int] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    total_potholes: int = 0
    average_risk: float = 0.0
    max_risk: float = 0.0
    detections: Optional[SeverityStats] = None
    description: Optional[str] = None


class ReportUpdate(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    description: Optional[str] = None


class ReportDraftCreatedResponse(BaseModel):
    uuid: uuid.UUID
    status: str
    priority: str
    can_be_submitted: bool
    message: str = "Черновик заявки создан"


class ReportResponse(BaseModel):
    uuid: uuid.UUID
    user_id: Optional[int]
    latitude: Optional[str]
    longitude: Optional[str]
    address: Optional[str]
    image_url: Optional[str]
    image_urls: Optional[Dict]
    video_url: Optional[str]
    total_potholes: int
    average_risk: float
    max_risk: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    status: str
    priority: str
    description: Optional[str]
    comment: Optional[str]
    created_at: datetime
    submitted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ai_agent_task_id: Optional[str] = None
    ai_agent_status: Optional[str] = None
    organization_name: Optional[str] = None
    external_tracking_id: Optional[str] = None

    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    uuid: uuid.UUID
    user_id: Optional[int]
    latitude: Optional[str]
    longitude: Optional[str]
    address: Optional[str]
    status: str
    priority: str
    total_potholes: int
    max_risk: float
    created_at: datetime
    image_url: Optional[str] = None
    image_urls: Optional[Dict] = None
    video_url: Optional[str] = None
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    total: int
    items: List[ReportListItem]


class ReportSubmitResponse(BaseModel):
    """Ответ при отправке заявки"""
    uuid: uuid.UUID
    status: str
    priority: str
    message: str
    ai_agent_task_id: Optional[str] = None
    estimated_processing_time: int = 300
