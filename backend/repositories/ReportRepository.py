# ReportRepository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from backend.models.report_model import Report


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, report: Report) -> Report:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_by_uuid(self, report_uuid: uuid.UUID) -> Optional[Report]:
        result = await self.db.execute(
            select(Report).where(Report.uuid == report_uuid)
        )
        return result.scalar_one_or_none()