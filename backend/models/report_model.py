
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Float, Boolean, JSON, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import enum
import uuid

from backend.core.database import Base


class ReportStatus(str, enum.Enum):
    """Статус заявки"""
    DRAFT = "draft"              # Черновик (на редактировании)
    SUBMITTED = "submitted"      # Отправлена
    IN_REVIEW = "in_review"      # На рассмотрении
    IN_PROGRESS = "in_progress"  # В работе
    COMPLETED = "completed"      # Завершена

class ReportPriority(str, enum.Enum):
    """Приоритет заявки"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Report(Base):
    """Модель заявки на ремонт дорожного покрытия"""
    __tablename__ = "reports"

    # UUID как первичный ключ
    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )


    user_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Медиафайлы
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    image_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Результаты анализа
    total_potholes: Mapped[int] = mapped_column(Integer, default=0)
    max_risk: Mapped[float] = mapped_column(Float, default=0.0)

    # Статус и приоритет
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        default=ReportStatus.DRAFT,
        nullable=False,
        index=True
    )
    priority: Mapped[ReportPriority] = mapped_column(
        Enum(ReportPriority),
        default=ReportPriority.MEDIUM,
        nullable=False,
        index=True
    )

    # Дополнительная информация
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


    def __repr__(self):
        return f"<Report(id={self.id}, status={self.status}, address={self.address})>"

    @property
    def is_draft(self) -> bool:
        """Проверка, является ли заявка черновиком"""
        return self.status == ReportStatus.DRAFT

    @property
    def auto_priority(self) -> ReportPriority:
        """Автоматическое определение приоритета"""
        if self.critical_count > 0 or self.max_risk > 70:
            return ReportPriority.CRITICAL
        elif self.high_count > 0 or self.max_risk > 50:
            return ReportPriority.HIGH
        elif self.medium_count > 0 or self.max_risk > 30:
            return ReportPriority.MEDIUM
        else:
            return ReportPriority.LOW


