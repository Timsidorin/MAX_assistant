# services/report_service.py
from pathlib import Path
from urllib.parse import urlparse

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime
import uuid

from backend.depends import get_email_service, get_document_service, get_gigachat_service
from backend.models.report_model import ReportStatus, ReportPriority, Report
from backend.schemas.report_schema import (
    ReportCreateDraft, ReportUpdate,
    ReportDraftCreatedResponse, ReportResponse, ReportSubmitResponse,
    ReportListResponse, ReportListItem, SeverityStats
)
from backend.repositories.ReportRepository import ReportRepository
from backend.services.ai_agent_service import find_road_agency_contacts


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReportRepository(db)

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
            submitted_at=report.submitted_at,
            updated_at=report.updated_at,
            ai_agent_task_id=report.ai_agent_task_id,
            ai_agent_status=report.ai_agent_status,
            organization_name=report.organization_name,
            external_tracking_id=report.external_tracking_id
        )

    async def update_draft(
            self,
            report_uuid: uuid.UUID,
            data: ReportUpdate
    ) -> ReportResponse:
        """Обновить черновик заявки"""
        report = await self.repository.get_by_uuid(report_uuid)

        if not report:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
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

        return await self.get_by_uuid(report_uuid)

    async def submit_report(self, report_uuid: uuid.UUID, background_tasks: BackgroundTasks) -> ReportSubmitResponse:
        """Отправка заявки с генерацией текста и отправкой email."""
        report = await self.repository.get_by_uuid(report_uuid)

        if not report:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail=f"Заявка уже отправлена. Текущий статус: {report.status.value}"
            )

        can_submit = report.can_be_submitted
        if not can_submit:
            raise HTTPException(
                status_code=400,
                detail="Заявка не готова к отправке. Заполните все обязательные поля."
            )

        # Обновляем статус
        report.status = ReportStatus.SUBMITTED
        report.submitted_at = datetime.now()

        # Создаем задачу для агента
        task_id = str(uuid.uuid4())
        report.ai_agent_task_id = task_id
        report.ai_agent_status = "processing"

        report = await self.repository.update(report)

        # Запускаем фоновую задачу
        background_tasks.add_task(
            self._process_and_send_complaint,
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

    async def _process_and_send_complaint(self, report_uuid: uuid.UUID, task_id: str):
        """Фоновая обработка: поиск контактов, генерация, отправка с фото."""
        try:
            report = await self.repository.get_by_uuid(report_uuid)
            # 1. Поиск контактов
            print(f"[Report Service] Step 1: Finding contacts...")
            contacts_result = find_road_agency_contacts(report.address)

            if not contacts_result.get('success') or not contacts_result.get('email'):
                report.ai_agent_status = "failed"
                report.comment = "Не удалось найти email для обращения"
                await self.repository.update(report)
                return

            organization_name = contacts_result.get('organization', 'Управление дорожной деятельности')
            # email_to = contacts_result['email']
            email_to = "timofeisidorin@vk.com"

            report.organization_name = organization_name
            await self.repository.update(report)

            print(f"[Report Service] Found email: {email_to}")

            # 2. Генерация текста через GigaChat
            print(f"[Report Service] Step 2: Generating complaint text...")
            gigachat = get_gigachat_service()

            complaint_text = gigachat.generate_complaint_text(
                city=contacts_result.get('city', 'Неизвестно'),
                address=report.address,
                description=report.description or "Обнаружены дефекты дорожного покрытия",
                total_potholes=report.total_potholes,
                max_risk=report.max_risk,
                priority=report.priority.value
            )

            # 3. Создание PDF документа
            print(f"[Report Service] Step 3: Creating document and converting to PDF...")
            doc_service = get_document_service()

            street = self._extract_street(report.address)

            file_bytes, file_ext = doc_service.create_complaint_document(
                city=contacts_result.get('city', 'Неизвестно'),
                street=street,
                organization_name=organization_name,
                person_name="Гражданин",
                count_photos=self._count_photos(report),
                year=datetime.now().year,
                convert_to_pdf=True
            )

            filename = f"zayavlenie_{report.uuid}.{file_ext}"

            # 4. Скачивание фотографий
            print(f"[Report Service] Step 4: Downloading photos...")
            photo_attachments = await self._download_photos(report)

            # 5. Формируем все вложения
            attachments = [
                (filename, file_bytes)  # PDF/DOCX заявление
            ]
            attachments.extend(photo_attachments)  # Добавляем фото

            print(f"[Report Service] Total attachments: {len(attachments)}")

            # 6. Отправка email
            print(f"[Report Service] Step 5: Sending email...")
            email_service = get_email_service()

            subject = f"Заявление о дефектах дорожного покрытия - {report.address}"

            success = email_service.send_complaint_email(
                to_email=email_to,
                subject=subject,
                body_text=complaint_text,
                attachments=attachments
            )

            if success:
                report.ai_agent_status = "completed"
                report.status = ReportStatus.IN_REVIEW
                report.comment = f"Заявление отправлено на {email_to} с {len(photo_attachments)} фото"
                print(f"[Report Service] ✅ Successfully sent to {email_to}")
            else:
                report.ai_agent_status = "failed"
                report.comment = "Ошибка при отправке email"
                print(f"[Report Service] ❌ Failed to send email")

            await self.repository.update(report)

        except Exception as e:
            print(f"[Report Service] ❌ Error: {e}")
            try:
                report = await self.repository.get_by_uuid(report_uuid)
                if report:
                    report.ai_agent_status = "failed"
                    report.comment = f"Ошибка: {str(e)}"
                    await self.repository.update(report)
            except:
                pass

    async def _download_photos(self, report: Report) -> list:
        """
        Скачивает все фотографии из report.image_urls.

        Returns:
            list: [(filename, file_bytes), ...]
        """
        photo_attachments = []

        # Собираем все URL фотографий
        photo_urls = []

        if report.image_url:
            photo_urls.append(report.image_url)

        if report.image_urls and isinstance(report.image_urls, dict):
            # image_urls может быть: {"urls": ["url1", "url2", ...]}
            if 'urls' in report.image_urls:
                photo_urls.extend(report.image_urls['urls'])
            # Или просто список: ["url1", "url2", ...]
            elif isinstance(report.image_urls, list):
                photo_urls.extend(report.image_urls)

        print(f"[Report Service] Found {len(photo_urls)} photo URLs")
        for idx, url in enumerate(photo_urls, 1):
            try:
                print(f"[Report Service] Downloading photo {idx}/{len(photo_urls)}: {url[:50]}...")

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Определяем расширение файла
                parsed_url = urlparse(url)
                file_ext = Path(parsed_url.path).suffix or '.jpg'

                # Формируем имя файла
                filename = f"photo_{idx}{file_ext}"

                photo_attachments.append((filename, response.content))
                print(f"[Report Service] Downloaded: {filename} ({len(response.content)} bytes)")

            except Exception as e:
                print(f"[Report Service] ⚠️ Failed to download photo {idx}: {e}")
                continue

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

        return ReportListResponse(total=total, items=items)

    async def delete_draft(self, report_uuid: uuid.UUID) -> dict:
        """Удалить черновик"""
        report = await self.repository.get_by_uuid(report_uuid)

        if not report:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        if report.status != ReportStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Можно удалять только черновики"
            )

        await self.repository.delete(report)

        return {
            "message": "Черновик удален",
            "uuid": str(report_uuid)
        }

    async def get_user_reports(
            self,
            user_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> ReportListResponse:
        """Получить все заявки пользователя"""
        return await self.get_list(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    async def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику заявок пользователя"""
        reports, total = await self.repository.get_list(user_id=user_id, limit=1000)

        stats = {
            "total": total,
            "by_status": {
                "draft": 0,
                "submitted": 0,
                "in_review": 0,
                "in_progress": 0,
                "completed": 0
            },
            "by_priority": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "total_potholes_reported": 0,
            "average_risk": 0.0
        }

        risk_sum = 0
        for report in reports:
            stats["by_status"][report.status.value] += 1
            stats["by_priority"][report.priority.value] += 1
            stats["total_potholes_reported"] += report.total_potholes
            risk_sum += report.average_risk

        if total > 0:
            stats["average_risk"] = round(risk_sum / total, 2)

        return stats
