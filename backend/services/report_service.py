from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse
import logging
import uuid

import aiohttp
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import async_session_maker
from backend.models.report_model import ReportStatus, ReportPriority, Report
from backend.repositories.ReportRepository import ReportRepository
from backend.schemas.report_schema import (
    ExternalSubmissionConfirm,
    ReportCreateDraft,
    ReportDraftCreatedResponse,
    ReportGeoPoint,
    ReportListResponse,
    ReportListItem,
    ReportResponse,
    ReportStatsResponse,
    ReportSubmitResponse,
    ReportUpdate,
)
from backend.services.ai_agent_service import find_road_agency_contacts
from backend.services.document_service import DocumentService
from backend.services.external_services.email_service import EmailService
from backend.services.external_services.geo_service import GeocodingService
from backend.services.external_services.gigachat_service import GigaChatService
from backend.services.external_services.local_storage_service import LocalStorageService
from backend.services.notification_service import notify_user
from backend.services.users_service import UserService

logger = logging.getLogger(__name__)


POINTS_BY_PRIORITY = {
    ReportPriority.LOW: 10,
    ReportPriority.MEDIUM: 20,
    ReportPriority.HIGH: 50,
    ReportPriority.CRITICAL: 100,
}


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReportRepository(db)
        self._email_service: Optional[EmailService] = None
        self._document_service: Optional[DocumentService] = None
        self._gigachat_service: Optional[GigaChatService] = None

    @property
    def email_service(self) -> EmailService:
        if self._email_service is None:
            self._email_service = EmailService()
        return self._email_service

    @property
    def document_service(self) -> DocumentService:
        if self._document_service is None:
            self._document_service = DocumentService()
        return self._document_service

    @property
    def gigachat_service(self) -> GigaChatService:
        if self._gigachat_service is None:
            self._gigachat_service = GigaChatService()
        return self._gigachat_service

    async def create_draft(self, data: ReportCreateDraft) -> ReportDraftCreatedResponse:
        latitude, longitude = await self._normalize_coordinates(
            data.latitude, data.longitude, data.address
        )

        report = Report(
            user_id=data.user_id,
            latitude=latitude,
            longitude=longitude,
            address=data.address,
            description=data.description,
            status=ReportStatus.DRAFT,
            image_url=data.image_url,
            image_urls={"urls": data.image_urls} if data.image_urls else None,
            video_url=data.video_url,
            total_potholes=data.total_potholes,
            average_risk=data.average_risk,
            max_risk=data.max_risk,
            critical_count=data.detections.CRITICAL if data.detections else 0,
            high_count=data.detections.HIGH if data.detections else 0,
            medium_count=data.detections.MEDIUM if data.detections else 0,
            low_count=data.detections.LOW if data.detections else 0,
        )
        report.priority = report.auto_priority
        report = await self.repository.create(report)

        logger.info(f"Draft report created: {report.uuid}, can_submit={report.can_be_submitted}")
        return ReportDraftCreatedResponse(
            uuid=report.uuid,
            status=report.status.value,
            priority=report.priority.value,
            can_be_submitted=report.can_be_submitted,
            message="Черновик заявки создан",
        )

    async def _normalize_coordinates(
        self,
        latitude: Optional[str],
        longitude: Optional[str],
        address: Optional[str],
    ) -> tuple[Optional[str], Optional[str]]:
        try:
            coordinates_missing = not latitude or not longitude or (
                float(latitude) == 0 and float(longitude) == 0
            )
        except (TypeError, ValueError):
            coordinates_missing = True

        if not coordinates_missing:
            return latitude, longitude

        if not address:
            return None, None

        resolved = await GeocodingService().geocode_address(address)
        return resolved if resolved else (None, None)

    async def get_by_uuid(self, report_uuid: uuid.UUID) -> ReportResponse:
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found")
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return ReportResponse.model_validate(report)

    async def update_draft(self, report_uuid: uuid.UUID, data: ReportUpdate) -> ReportResponse:
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found for update")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            logger.warning(f"Cannot edit report {report_uuid} with status {report.status.value}")
            raise HTTPException(
                status_code=400,
                detail=f"Нельзя редактировать заявку со статусом {report.status.value}",
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

    async def submit_report(
        self,
        report_uuid: uuid.UUID,
        background_tasks: BackgroundTasks,
    ) -> ReportSubmitResponse:
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found for submission")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        is_retry = report.status == ReportStatus.SUBMITTED and report.ai_agent_status == "failed"
        if report.status != ReportStatus.DRAFT and not is_retry:
            logger.warning(f"Report {report_uuid} already submitted with status {report.status.value}")
            raise HTTPException(
                status_code=400,
                detail=f"Заявка уже отправлена. Текущий статус: {report.status.value}",
            )

        if not report.can_be_submitted:
            logger.warning(f"Report {report_uuid} not ready for submission")
            raise HTTPException(
                status_code=400,
                detail="Заявка не готова к отправке. Заполните все обязательные поля.",
            )

        report.status = ReportStatus.SUBMITTED
        if not is_retry:
            report.submitted_at = datetime.now(timezone.utc)

        await self._award_points(report)

        task_id = str(uuid.uuid4())
        report.ai_agent_task_id = task_id
        report.ai_agent_status = "processing"
        report = await self.repository.update(report)
        logger.info(f"Report {report_uuid} submitted, task_id={task_id}")

        if report.user_id:
            await notify_user(
                report.user_id,
                f"📨 Заявка по адресу «{report.address}» принята в обработку!\n"
                f"Приоритет: {report.priority.value}. Ищем контакты ответственной организации…",
            )

        background_tasks.add_task(
            self._process_and_send_complaint_wrapper,
            report_uuid=report.uuid,
            task_id=task_id,
        )

        return ReportSubmitResponse(
            uuid=report.uuid,
            status=report.status.value,
            priority=report.priority.value,
            message="Заявка принята в обработку. Производится поиск контактов и генерация текста.",
            ai_agent_task_id=task_id,
            estimated_processing_time=60,
        )

    async def _award_points(self, report: Report) -> None:
        if not report.user_id:
            return

        points = POINTS_BY_PRIORITY.get(report.priority, 10)
        try:
            user_service = UserService(self.db)
            updated_user = await user_service.update_user_points(report.user_id, points)
            if updated_user:
                logger.info(f"User {report.user_id} awarded {points} points for report {report.uuid}")
            else:
                logger.warning(f"Failed to update points for user {report.user_id}")
        except Exception as e:
            logger.error(f"Error updating user {report.user_id} points: {e}", exc_info=True)

    async def _process_and_send_complaint_wrapper(self, report_uuid: uuid.UUID, task_id: str) -> None:
        async with async_session_maker() as session:
            try:
                await self._process_and_send_complaint(session, report_uuid, task_id)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"[Task {task_id}] Error in wrapper: {e}", exc_info=True)
            finally:
                await session.close()

    async def _process_and_send_complaint(
        self,
        session: AsyncSession,
        report_uuid: uuid.UUID,
        task_id: str,
    ) -> None:
        repository = ReportRepository(session)
        report = await repository.get_by_uuid(report_uuid)
        if not report:
            logger.error(f"[Task {task_id}] Report {report_uuid} not found")
            return

        try:
            logger.info(f"[Task {task_id}] Finding contacts for address: {report.address}")
            contacts = find_road_agency_contacts(report.address)

            organization_name = contacts.get("organization") or "Управление дорожной деятельности"
            email = contacts.get("email")
            phone = contacts.get("phone")
            website = contacts.get("website")
            source = contacts.get("source") or "fallback"

            report.organization_name = organization_name
            report.organization_email = email
            report.organization_phone = phone
            report.organization_website = website
            report.contact_source = source

            person_name = await self._resolve_person_name(session, report.user_id)
            file_bytes, file_ext = self.document_service.create_complaint_document(
                city=contacts.get("city", ""),
                street=self._extract_street(report.address),
                organization_name=organization_name,
                person_name=person_name,
                count_photos=self._count_photos(report),
                year=datetime.now().year,
                convert_to_pdf=True,
            )
            if not file_bytes:
                raise ValueError("Generated document is empty")

            if not email:
                channel_type = contacts.get("channel_type") or "manual"
                logger.info(
                    f"[Task {task_id}] Official channel selected for {organization_name}: "
                    f"type={channel_type}, url={website}, source={source}"
                )
                document_url = await LocalStorageService().upload_file(
                    file_bytes,
                    folder="complaints",
                    filename=f"zayavlenie_{report.uuid}.{file_ext}",
                    content_type=(
                        "application/pdf"
                        if file_ext == "pdf"
                        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ),
                    base_url=self._public_base_url(report),
                )
                stored_media = dict(report.image_urls or {})
                stored_media["document_url"] = document_url
                report.image_urls = stored_media
                report.ai_agent_status = "awaiting_user_submission" if website else "manual"
                report.status = ReportStatus.IN_REVIEW
                report.comment = self._build_manual_comment(
                    organization_name,
                    phone,
                    website,
                    channel_type,
                    contacts.get("reason"),
                )
                await repository.update(report)
                await self._notify_manual(report, channel_type, contacts.get("reason"))
                return

            complaint_text = self.gigachat_service.generate_complaint_text(
                city=contacts.get("city", "Неизвестно"),
                address=report.address,
                description=report.description or "Обнаружены дефекты дорожного покрытия",
                total_potholes=report.total_potholes,
                max_risk=report.max_risk,
                priority=report.priority.value,
                person_name=person_name,
            )

            photo_attachments = await self._download_photos(report)
            attachments = [(f"zayavlenie.{file_ext}", file_bytes)]
            attachments.extend(photo_attachments)

            logger.info(f"[Task {task_id}] Sending email to {email}")
            success = self.email_service.send_complaint_email(
                to_email=email,
                subject=f"Заявление о дефектах дорожного покрытия - {report.address}",
                body_text=complaint_text,
                attachments=attachments,
            )

            if success:
                report.ai_agent_status = "completed"
                report.status = ReportStatus.IN_REVIEW
                report.comment = f"Заявление отправлено на {email} с {len(photo_attachments)} фото"
                await repository.update(report)
                if source == "fallback":
                    await self._notify_fallback_sent(report, organization_name, contacts)
                else:
                    await self._notify_sent(report, organization_name)
                logger.info(f"[Task {task_id}] Successfully sent to {email}")
            else:
                report.ai_agent_status = "failed"
                report.comment = "Ошибка при отправке email"
                await repository.update(report)
                await self._notify_failed(report, "не удалось отправить письмо")
                logger.error(f"[Task {task_id}] Failed to send email")

        except Exception as e:
            logger.error(f"[Task {task_id}] Error processing report {report_uuid}: {e}", exc_info=True)
            await self._mark_failed(repository, report, str(e))

    async def _resolve_person_name(self, session: AsyncSession, user_id: Optional[int]) -> str:
        if not user_id:
            return "Заявитель"

        try:
            user_service = UserService(session)
            user = await user_service.get_user_by_max_user_id(user_id)
            if user and user.first_name and user.last_name:
                return f"{user.first_name} {user.last_name}"
        except Exception as e:
            logger.error(f"Error getting user data: {e}", exc_info=True)
        return "Заявитель"

    def _build_manual_comment(
        self,
        organization_name: Optional[str],
        phone: Optional[str],
        website: Optional[str],
        channel_type: str = "manual",
        reason: Optional[str] = None,
    ) -> str:
        parts = [
            f"Выбран канал {channel_type}: {organization_name or 'организация не определена'}."
        ]
        if reason:
            parts.append(f"Основание: {reason}")
        if phone:
            parts.append(f"Телефон: {phone}")
        if website:
            parts.append(f"Официальный канал: {website}")
        parts.append("Автоматическая email-отправка не выполнялась.")
        return " ".join(parts)

    async def _notify_manual(
        self,
        report: Report,
        channel_type: str = "manual",
        reason: Optional[str] = None,
    ) -> None:
        if not report.user_id:
            return
        msg = (
            f"Заявление по адресу «{report.address}» подготовлено.\n"
            f"Организация: {report.organization_name or 'не определена'}\n"
            f"Тип канала: {channel_type}\n"
            f"Основание маршрутизации: {reason or 'поиск ответственного дорожного органа'}\n\n"
            "Скачайте заявление, откройте официальную приёмную, прикрепите документ и фотографии. "
            "После подачи подтвердите отправку в разделе заявок."
        )
        links = []
        if report.document_url:
            links.append(("Скачать заявление", report.document_url))
        if report.organization_website:
            links.append(("Открыть приёмную", report.organization_website))
        await notify_user(report.user_id, msg, links=links)

    async def _notify_sent(self, report: Report, organization_name: str) -> None:
        if not report.user_id:
            return
        msg = (
            f"✅ Готово! Заявление о дефектах по адресу «{report.address}» "
            f"отправлено в «{organization_name}».\n"
            "Очки ямоборца уже начислены — проверь профиль 🏆"
        )
        await notify_user(report.user_id, msg)

    async def _notify_fallback_sent(
        self,
        report: Report,
        organization_name: str,
        contacts: dict,
    ) -> None:
        if not report.user_id:
            return
        website = contacts.get("website") or "сайт не найден"
        phone = contacts.get("phone") or "телефон не найден"
        msg = (
            f"✅ Заявление по адресу «{report.address}» сохранено.\n"
            f"Найдена организация: «{organization_name}».\n"
            f"Официальный email ведомства в открытых источниках не обнаружен.\n"
            f"Контакты: {website}, {phone}.\n"
            "Заявление направлено на резервный канал для дальнейшей маршрутизации."
        )
        await notify_user(report.user_id, msg)

    async def _notify_failed(self, report: Report, reason: str) -> None:
        if not report.user_id:
            return
        msg = (
            f"⚠️ Не удалось отправить заявление по адресу «{report.address}»: {reason}. "
            "Попробуйте повторить позже."
        )
        await notify_user(report.user_id, msg)

    async def _mark_failed(
        self,
        repository: ReportRepository,
        report: Report,
        reason: str,
    ) -> None:
        report.ai_agent_status = "failed"
        report.comment = f"Ошибка: {reason}"
        try:
            await repository.update(report)
        except Exception as update_error:
            logger.error(f"Failed to update report status: {update_error}", exc_info=True)
        if report.user_id:
            await self._notify_failed(report, "внутренняя ошибка обработки")

    async def _download_photos(self, report: Report) -> List[tuple]:
        photo_urls = self._collect_photo_urls(report)
        if not photo_urls:
            return []

        local_storage = LocalStorageService()
        photo_attachments = []

        async with aiohttp.ClientSession() as session:
            for idx, url in enumerate(photo_urls, 1):
                try:
                    parsed_url = urlparse(url)
                    file_ext = Path(parsed_url.path).suffix or ".jpg"
                    filename = f"photo_{idx}{file_ext}"

                    content = await local_storage.read_file(url)
                    if content is None:
                        async with session.get(
                            url,
                            timeout=aiohttp.ClientTimeout(total=30),
                        ) as response:
                            response.raise_for_status()
                            content = await response.read()

                    photo_attachments.append((filename, content))
                except Exception as e:
                    logger.warning(f"Failed to load photo {idx} from {url[:50]}: {e}")

        return photo_attachments

    def _collect_photo_urls(self, report: Report) -> List[str]:
        urls = []
        if report.image_url:
            urls.append(report.image_url)

        stored = report.image_urls
        if isinstance(stored, dict):
            urls.extend(stored.get("urls") or [])
        elif isinstance(stored, list):
            urls.extend(stored)

        return urls

    def _public_base_url(self, report: Report) -> str:
        for url in self._collect_photo_urls(report):
            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        return ""

    def _count_photos(self, report: Report) -> int:
        return len(self._collect_photo_urls(report))

    def _extract_street(self, address: str) -> str:
        parts = address.split(",")
        street_parts = []
        for part in parts:
            part = part.strip()
            if any(kw in part.lower() for kw in ["ул", "пр", "д", "дом", "корп"]):
                street_parts.append(part)
        return ", ".join(street_parts) if street_parts else address

    async def get_list(
        self,
        user_id: Optional[int] = None,
        status: Optional[ReportStatus] = None,
        priority: Optional[ReportPriority] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ReportListResponse:
        reports, total = await self.repository.get_list(
            user_id=user_id,
            status=status,
            priority=priority,
            skip=skip,
            limit=limit,
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
                video_url=r.video_url,
                submitted_at=r.submitted_at,
                organization_name=r.organization_name,
                organization_email=r.organization_email,
                organization_website=r.organization_website,
                contact_source=r.contact_source,
                ai_agent_status=r.ai_agent_status,
                document_url=r.document_url,
            )
            for r in reports
        ]

        logger.debug(f"Retrieved {len(items)}/{total} reports")
        return ReportListResponse(total=total, items=items)

    async def get_geo_list(self) -> List[ReportGeoPoint]:
        reports = await self.repository.get_geo_list()
        points = []
        for r in reports:
            try:
                points.append(ReportGeoPoint(
                    uuid=r.uuid,
                    latitude=float(r.latitude),
                    longitude=float(r.longitude),
                    address=r.address,
                    status=r.status.value,
                    priority=r.priority.value,
                    max_risk=r.max_risk,
                    total_potholes=r.total_potholes,
                    confirmations=r.confirmations or 0,
                    created_at=r.created_at,
                ))
            except (TypeError, ValueError):
                logger.warning(f"Skipping report {r.uuid} with invalid coordinates")
        return points

    async def get_stats(self) -> ReportStatsResponse:
        stats = await self.repository.get_stats()
        return ReportStatsResponse(**stats)

    async def confirm_external_submission(
        self,
        report_uuid: uuid.UUID,
        data: ExternalSubmissionConfirm,
    ) -> ReportResponse:
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        if report.user_id != data.user_id:
            raise HTTPException(status_code=403, detail="Заявка принадлежит другому пользователю")
        if report.ai_agent_status != "awaiting_user_submission":
            raise HTTPException(status_code=400, detail="Заявка не ожидает подтверждения отправки")

        report.ai_agent_status = "user_submitted"
        details = "Пользователь подтвердил отправку через официальную приёмную."
        if data.registration_number:
            details += f" Регистрационный номер: {data.registration_number.strip()}"
        report.comment = f"{report.comment or ''} {details}".strip()
        await self.repository.update(report)
        if report.user_id:
            await notify_user(
                report.user_id,
                "Отправка обращения подтверждена. Сохраните регистрационный номер и ответ ведомства.",
            )
        return ReportResponse.model_validate(report)

    async def confirm_report(self, report_uuid: uuid.UUID) -> dict:
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        if report.status == ReportStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Нельзя подтвердить черновик")

        report.confirmations = (report.confirmations or 0) + 1
        report.priority = report.auto_priority
        await self.repository.update(report)
        logger.info(f"Report {report_uuid} confirmed, total confirmations={report.confirmations}")
        return {
            "uuid": str(report_uuid),
            "confirmations": report.confirmations,
            "priority": report.priority.value,
        }

    async def delete_draft(self, report_uuid: uuid.UUID) -> dict:
        report = await self.repository.get_by_uuid(report_uuid)
        if not report:
            logger.warning(f"Report {report_uuid} not found for deletion")
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            logger.warning(f"Cannot delete non-draft report {report_uuid} with status {report.status.value}")
            raise HTTPException(
                status_code=400,
                detail="Можно удалять только черновики",
            )

        await self.repository.delete(report)
        logger.info(f"Draft report {report_uuid} deleted")
        return {
            "message": "Черновик удален",
            "uuid": str(report_uuid),
        }
