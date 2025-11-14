from pathlib import Path
from urllib.parse import urlparse
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, BackgroundTasks
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from backend.core.config import configs
from backend.core.database import async_session_maker  # Импортируем session_maker
from backend.models.report_model import ReportStatus, ReportPriority, Report
from backend.schemas.report_schema import (
    ReportCreateDraft, ReportUpdate,
    ReportDraftCreatedResponse, ReportResponse, ReportSubmitResponse,
    ReportListResponse, ReportListItem
)

from backend.repositories.ReportRepository import ReportRepository
from backend.services.ai_agent_service import find_road_agency_contacts
from backend.services.users_service import UserService
from backend.services.external_services.email_service import EmailService
from backend.services.external_services.gigachat_service import GigaChatService
from backend.services.document_service import DocumentService
from backend.schemas.users_schema import UserUpdate

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReportRepository(db)
        # Инициализируем singleton сервисы как атрибуты класса
        self._email_service = None
        self._document_service = None
        self._gigachat_service = None

    @property
    def email_service(self) -> EmailService:
        """Lazy init для EmailService"""
        if self._email_service is None:
            self._email_service = EmailService()
        return self._email_service

    @property
    def document_service(self) -> DocumentService:
        """Lazy init для DocumentService"""
        if self._document_service is None:
            self._document_service = DocumentService()
        return self._document_service

    @property
    def gigachat_service(self) -> GigaChatService:
        """Lazy init для GigaChatService"""
        if self._gigachat_service is None:
            self._gigachat_service = GigaChatService()
        return self._gigachat_service

    async def create_draft(self, data: ReportCreateDraft) -> ReportDraftCreatedResponse:
        """Создать черновик заявки"""
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

        logger.info(f"Draft report created: {report.uuid}, can_submit={can_submit}")
        return ReportDraftCreatedResponse(
            uuid=report.uuid,
            status=report.status.value,
            priority=report.priority.value,
            can_be_submitted=can_submit,
            message="Черновик заявки создан"
        )

    async def get_by_uuid(self, report_uuid: uuid.UUID) -> ReportResponse:
        """Получить заявку по UUID"""
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        return ReportResponse(
            uuid=report.uuid,
            user_id=report.user_id,
            latitude=report.latitude,
            longitude=report.longitude,
            address=report.address,
            image_url=report.image_url,
            image_urls=report.image_urls,
            video_url=report.video_url,
            total_potholes=report.total_potholes,
            average_risk=report.average_risk,
            max_risk=report.max_risk,
            critical_count=report.critical_count,
            high_count=report.high_count,
            medium_count=report.medium_count,
            low_count=report.low_count,
            status=report.status.value,
            priority=report.priority.value,
            description=report.description,
            comment=report.comment,
            created_at=report.created_at,
        )

    async def update_draft(
            self,
            report_uuid: uuid.UUID,
            data: ReportUpdate
    ) -> ReportResponse:
        """Обновить черновик заявки"""
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found for update")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            logger.warning(f"Cannot edit report {report_uuid} with status {report.status.value}")
            raise HTTPException(
                status_code=400,
                detail=f"Нельзя редактировать заявку со статусом {report.status.value}"
            )

        update_data = data.model_dump(exclude_unset=True)
        if "image_urls" in update_data and update_data["image_urls"]:
            update_data["image_urls"] = {"urls": update_data["image_urls"]}

        for field, value in update_data.items():
            setattr(report, field, value)

        report.priority = report.auto_priority
        report = await self.repository.update(report)
        logger.info(f"Report {report_uuid} updated successfully")
        return await self.get_by_uuid(report_uuid)

    async def submit_report(self, report_uuid: uuid.UUID, background_tasks: BackgroundTasks) -> ReportSubmitResponse:
        """Отправка заявки с генерацией текста и отправкой email."""
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found for submission")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            logger.warning(f"Report {report_uuid} already submitted with status {report.status.value}")
            raise HTTPException(
                status_code=400,
                detail=f"Заявка уже отправлена. Текущий статус: {report.status.value}"
            )

        can_submit = report.can_be_submitted
        if not can_submit:
            logger.warning(f"Report {report_uuid} not ready for submission")
            raise HTTPException(
                status_code=400,
                detail="Заявка не готова к отправке. Заполните все обязательные поля."
            )

        report.status = ReportStatus.SUBMITTED
        report.submitted_at = datetime.now()

        if report.user_id:
            try:
                user_service = UserService(self.db)
                points_awarded = {
                    ReportPriority.LOW: 10,
                    ReportPriority.MEDIUM: 20,
                    ReportPriority.HIGH: 50,
                    ReportPriority.CRITICAL: 100
                }.get(report.priority, 10)

                updated_user = await user_service.update_user_points(report.user_id, points_awarded)
                if updated_user:
                    logger.info(f"User {report.user_id} awarded {points_awarded} points for report {report_uuid}")
                else:
                    logger.warning(f"Failed to update points for user {report.user_id}")
            except Exception as e:
                logger.error(f"Error updating user {report.user_id} points: {e}", exc_info=True)

        task_id = str(uuid.uuid4())
        report.ai_agent_task_id = task_id
        report.ai_agent_status = "processing"
        report = await self.repository.update(report)
        logger.info(f"Report {report_uuid} submitted, task_id={task_id}")

        background_tasks.add_task(
            self._process_and_send_complaint_wrapper,
            report_uuid=report.uuid,
            task_id=task_id
        )

        return ReportSubmitResponse(
            uuid=report.uuid,
            status=report.status.value,
            priority=report.priority.value,
            message="Заявка принята в обработку. Производится поиск контактов и генерация текста.",
            ai_agent_task_id=task_id,
            estimated_processing_time=60
        )

    async def _process_and_send_complaint_wrapper(self, report_uuid: uuid.UUID, task_id: str):
        """
        Wrapper для фоновой задачи - создаёт новую сессию БД.
        Это необходимо, так как фоновые задачи выполняются вне контекста запроса.
        """
        async with async_session_maker() as session:
            try:
                await self._process_and_send_complaint(session, report_uuid, task_id)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"[Task {task_id}] Error in wrapper: {e}", exc_info=True)
            finally:
                await session.close()

    async def _process_and_send_complaint(self, session: AsyncSession, report_uuid: uuid.UUID, task_id: str):
        """Фоновая обработка: поиск контактов, генерация, отправка с фото."""
        try:
            logger.info(f"[Task {task_id}] Starting background processing for report {report_uuid}")

            # Создаём новый repository с новой сессией
            repository = ReportRepository(session)
            report = await repository.get_by_uuid(report_uuid)

            if not report:
                logger.error(f"[Task {task_id}] Report {report_uuid} not found")
                return

            # Step 1: Find contacts
            logger.info(f"[Task {task_id}] Finding contacts for address: {report.address}")
            contacts_result = find_road_agency_contacts(report.address)

            if not contacts_result.get('success') or not contacts_result.get('email'):
                report.ai_agent_status = "failed"
                report.comment = "Не удалось найти email для обращения"
                await repository.update(report)
                logger.error(f"[Task {task_id}] Failed to find contacts")
                return

            organization_name = contacts_result.get('organization', 'Управление дорожной деятельности')
            email_to = "timofeisidorin@vk.com"  # For testing
            # email_to = contacts_result.get('email')  # Production

            report.organization_name = organization_name
            await repository.update(report)
            logger.info(f"[Task {task_id}] Found email: {email_to}, organization: {organization_name}")

            # Step 2: Get user name
            person_name = "Заявитель"
            if report.user_id:
                try:
                    user_service = UserService(session)
                    user = await user_service.get_user_by_max_user_id(report.user_id)
                    if user and user.first_name and user.last_name:
                        person_name = f"{user.first_name} {user.last_name}"
                    logger.debug(f"[Task {task_id}] User name: {person_name}")
                except Exception as e:
                    logger.error(f"[Task {task_id}] Error getting user data: {e}", exc_info=True)

            # Step 3: Generate complaint text
            logger.info(f"[Task {task_id}] Generating complaint text")
            complaint_text = self.gigachat_service.generate_complaint_text(
                city=contacts_result.get('city', 'Неизвестно'),
                address=report.address,
                description=report.description or "Обнаружены дефекты дорожного покрытия",
                total_potholes=report.total_potholes,
                max_risk=report.max_risk,
                priority=report.priority.value,
                person_name=person_name
            )

            # Step 4: Create document
            logger.info(f"[Task {task_id}] Creating complaint document")
            street = self._extract_street(report.address)
            file_bytes, file_ext = self.document_service.create_complaint_document(
                city=contacts_result.get("city", ""),
                street=street,
                organization_name=organization_name,
                person_name=person_name,
                count_photos=self._count_photos(report),
                year=datetime.now().year,
                convert_to_pdf=True
            )

            if len(file_bytes) == 0:
                raise ValueError("Generated document is empty")
            logger.info(f"[Task {task_id}] Document created: {len(file_bytes)} bytes")

            # Step 5: Download photos
            logger.info(f"[Task {task_id}] Downloading photos")
            photo_attachments = await self._download_photos(report)
            attachments = [(f"zayavlenie.{file_ext}", file_bytes)]
            attachments.extend(photo_attachments)
            logger.info(f"[Task {task_id}] Total attachments: {len(attachments)}")

            # Step 6: Send email
            logger.info(f"[Task {task_id}] Sending email to {email_to}")
            subject = f"Заявление о дефектах дорожного покрытия - {report.address}"
            success = self.email_service.send_complaint_email(
                to_email=email_to,
                subject=subject,
                body_text=complaint_text,
                attachments=attachments
            )

            if success:
                report.ai_agent_status = "completed"
                report.status = ReportStatus.IN_REVIEW
                report.comment = f"Заявление отправлено на {email_to} с {len(photo_attachments)} фото"
                logger.info(f"[Task {task_id}] Successfully sent to {email_to}")
            else:
                report.ai_agent_status = "failed"
                report.comment = "Ошибка при отправке email"
                logger.error(f"[Task {task_id}] Failed to send email")

            await repository.update(report)

        except Exception as e:
            logger.error(f"[Task {task_id}] Error processing report {report_uuid}: {e}", exc_info=True)
            try:
                repository = ReportRepository(session)
                report = await repository.get_by_uuid(report_uuid)
                if report:
                    report.ai_agent_status = "failed"
                    report.comment = f"Ошибка: {str(e)}"
                    await repository.update(report)
            except Exception as update_error:
                logger.error(f"[Task {task_id}] Failed to update report status: {update_error}", exc_info=True)

    async def _download_photos(self, report: Report) -> List[tuple]:
        """Скачивает все фотографии из report.image_urls."""
        photo_attachments = []
        photo_urls = []

        if report.image_url:
            photo_urls.append(report.image_url)

        if report.image_urls and isinstance(report.image_urls, dict):
            if 'urls' in report.image_urls:
                photo_urls.extend(report.image_urls['urls'])
        elif isinstance(report.image_urls, list):
            photo_urls.extend(report.image_urls)

        logger.info(f"Found {len(photo_urls)} photo URLs to download")

        async with aiohttp.ClientSession() as session:
            for idx, url in enumerate(photo_urls, 1):
                try:
                    logger.debug(f"Downloading photo {idx}/{len(photo_urls)}: {url[:50]}...")
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        response.raise_for_status()
                        content = await response.read()
                        parsed_url = urlparse(url)
                        file_ext = Path(parsed_url.path).suffix or '.jpg'
                        filename = f"photo_{idx}{file_ext}"
                        photo_attachments.append((filename, content))
                        logger.debug(f"Downloaded: {filename} ({len(content)} bytes)")
                except Exception as e:
                    logger.warning(f"Failed to download photo {idx} from {url[:50]}: {e}")
                    continue

        logger.info(f"Successfully downloaded {len(photo_attachments)}/{len(photo_urls)} photos")
        return photo_attachments

    def _count_photos(self, report: Report) -> int:
        """Подсчитывает количество фотографий."""
        count = 0
        if report.image_url:
            count += 1
        if report.image_urls and isinstance(report.image_urls, dict):
            if 'urls' in report.image_urls:
                count += len(report.image_urls['urls'])
        elif isinstance(report.image_urls, list):
            count += len(report.image_urls)
        return count

    def _extract_street(self, address: str) -> str:
        """Извлекает улицу из полного адреса."""
        parts = address.split(',')
        street_parts = []
        for part in parts:
            part = part.strip()
            if any(kw in part.lower() for kw in ['ул', 'пр', 'д', 'дом', 'корп']):
                street_parts.append(part)
        return ', '.join(street_parts) if street_parts else address

    async def get_list(
            self,
            user_id: Optional[int] = None,
            status: Optional[ReportStatus] = None,
            priority: Optional[ReportPriority] = None,
            skip: int = 0,
            limit: int = 50
    ) -> ReportListResponse:
        """Получить список заявок с фильтрацией"""
        reports, total = await self.repository.get_list(
            user_id=user_id,
            status=status,
            priority=priority,
            skip=skip,
            limit=limit
        )

        items = [
            ReportListItem(
                uuid=r.uuid,
                user_id=r.user_id,
                latitude=r.latitude,
                longitude=r.longitude,
                address=r.address,
                status=r.status.value,
                priority=r.priority.value,
                total_potholes=r.total_potholes,
                max_risk=r.max_risk,
                created_at=r.created_at,
                image_url=r.image_url,
                image_urls=r.image_urls,
                video_url=r.video_url
            )
            for r in reports
        ]

        logger.debug(f"Retrieved {len(items)}/{total} reports")
        return ReportListResponse(total=total, items=items)

    async def delete_draft(self, report_uuid: uuid.UUID) -> dict:
        """Удалить черновик"""
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found for deletion")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            logger.warning(f"Cannot delete non-draft report {report_uuid} with status {report.status.value}")
            raise HTTPException(
                status_code=400,
                detail="Можно удалять только черновики"
            )

        await self.repository.delete(report)
        logger.info(f"Draft report {report_uuid} deleted")
        return {
            "message": "Черновик удален",
            "uuid": str(report_uuid)
        }
