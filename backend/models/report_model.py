# report_model.py
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import enum
import uuid as uuid_lib

from backend.core.database import Base


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReportPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Report(Base):
    __tablename__ = "reports"

    uuid: Mapped[uuid_lib.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid_lib.uuid4,
        index=True
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.max_user_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    latitude: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    image_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    total_potholes: Mapped[int] = mapped_column(Integer, default=0)
    average_risk: Mapped[float] = mapped_column(Float, default=0.0)
    max_risk: Mapped[float] = mapped_column(Float, default=0.0)

    critical_count: Mapped[int] = mapped_column(Integer, default=0)
    high_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_count: Mapped[int] = mapped_column(Integer, default=0)
    low_count: Mapped[int] = mapped_column(Integer, default=0)

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

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Report(uuid={self.uuid}, status={self.status}, address={self.address})>"

    @property
    def is_draft(self) -> bool:
        return self.status == ReportStatus.DRAFT

    @property
    def can_be_submitted(self) -> bool:
        return (
            self.status == ReportStatus.DRAFT and
            self.latitude and
            self.longitude and
            self.address and
            (self.image_url or self.image_urls or self.video_url)
        )

    @property
    def auto_priority(self) -> ReportPriority:
        if self.critical_count > 0 or self.max_risk > 70:
            return ReportPriority.CRITICAL
        elif self.high_count > 0 or self.max_risk > 50:
            return ReportPriority.HIGH
        elif self.medium_count > 0 or self.max_risk > 30:
            return ReportPriority.MEDIUM
        else:
            return ReportPriority.LOW