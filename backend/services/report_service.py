# report_service.py
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.models.report_model import Report, ReportStatus, ReportPriority
from backend.schemas.report_schema import ReportCreateDraft, ReportDraftCreatedResponse
from backend.repositories.ReportRepository import ReportRepository


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReportRepository(db)

    async def create_draft(self, data: ReportCreateDraft) -> ReportDraftCreatedResponse:
        report = Report()
        report.user_id = data.user_id
        report.latitude = data.latitude
        report.longitude = data.longitude
        report.address = data.address
        report.description = data.description
        report.status = ReportStatus.DRAFT

        report.image_url = data.image_url
        if data.image_urls:
            report.image_urls = {"urls": data.image_urls}
        report.video_url = data.video_url

        report.total_potholes = data.total_potholes
        report.average_risk = data.average_risk
        report.max_risk = data.max_risk

        if data.detections:
            report.critical_count = data.detections.CRITICAL
            report.high_count = data.detections.HIGH
            report.medium_count = data.detections.MEDIUM
            report.low_count = data.detections.LOW

        report.priority = report.auto_priority

        report = await self.repository.create(report)

        can_submit = bool(
            report.status == ReportStatus.DRAFT and
            report.latitude and
            report.longitude and
            report.address and
            (report.image_url or report.image_urls or report.video_url)
        )

        return ReportDraftCreatedResponse(
            uuid=report.uuid,
            status=report.status.value,
            priority=report.priority.value,
            can_be_submitted=can_submit,
            message="Черновик заявки создан"
        )