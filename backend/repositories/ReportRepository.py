from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional, List, Tuple
import uuid as uuid_lib

from backend.models.report_model import Report, ReportStatus, ReportPriority

class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, report: Report) -> Report:
        """Создать новый отчет"""
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def get_by_uuid(self, report_uuid: uuid_lib.UUID) -> Optional[Report]:
        """Получить отчет по UUID"""
        stmt = select(Report).where(Report.uuid == report_uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, report: Report) -> Report:
        """Обновить существующий отчет"""
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def delete(self, report: Report) -> None:
        """Удалить отчет"""
        await self.db.delete(report)
        await self.db.commit()  # <-- ИЗМЕНЕНО с flush на commit


    async def get_list(
        self,
        user_id: Optional[int] = None,
        status: Optional[ReportStatus] = None,
        priority: Optional[ReportPriority] = None,
        skip: int = 0,
        limit: Optional[int] = 50
    ) -> Tuple[List[Report], int]:
        """
        Получить список отчетов с фильтрацией и пагинацией.
        Возвращает (список отчетов, общее количество).
        """
        stmt = select(Report)
        where_conditions = []

        if user_id is not None:
            where_conditions.append(Report.user_id == user_id)
        if status is not None:
            where_conditions.append(Report.status == status)
        if priority is not None:
            where_conditions.append(Report.priority == priority)

        if where_conditions:
            stmt = stmt.where(*where_conditions)

        stmt = stmt.order_by(Report.created_at.desc())
        if limit is not None:
            stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        reports = result.scalars().all()

        count_stmt = select(func.count(Report.uuid))
        if where_conditions:
            count_stmt = count_stmt.where(*where_conditions)

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        return reports, total

    async def count_submitted_reports_by_user(self, user_id: int) -> int:
        """Подсчет отправленных заявок пользователя"""
        stmt = select(func.count(Report.uuid)).where(
            Report.user_id == user_id,
            Report.status.in_([
                ReportStatus.SUBMITTED,
                ReportStatus.IN_REVIEW,
                ReportStatus.IN_PROGRESS,
                ReportStatus.COMPLETED
            ])
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
