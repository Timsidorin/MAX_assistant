from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from backend.core.database import Base


class User(Base):
    """
    Таблица пользователя
    """
    __tablename__ = "users"

    uuid: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    max_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    registration_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    sent_reports_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
