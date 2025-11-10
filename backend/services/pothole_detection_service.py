import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import tempfile
import os

from backend.schemas.cv_schema import (
    InputValues, DetectionResponse, MultipleDetectionResponse,
    VideoDetectionResponse, SeverityStats, SingleImageResult
)
from backend.services.external_services.geo_service import GeocodingService
from backend.services.external_services.s3_service import S3Service


class PotholeDetectionService:
    """Сервис для детекции ям на дорожном покрытии с YOLO11"""

    def __init__(self, model_path: str = './cv_models/best.pt', max_workers: int = 4):
        self.model_path = model_path
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.model = self._load_model()
        self.s3_service = S3Service()
        self.geocoding_service = GeocodingService()

        self.conf_threshold = 0.15
        self.iou_threshold = 0.5
        self.imgsz = 1280  # 640

    def _load_model(self):
        """Загрузка YOLO11 модели"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Модель не найдена: {self.model_path}")
            model = YOLO(self.model_path)
            return model
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            return None

    def is_model_loaded(self) -> bool:
        """Проверка загрузки модели"""
        return self.model is not None

    @staticmethod
    def calculate_pothole_risk_score(
            box_area: float,
            image_area: float,
            confidence: float,
            position_y: int,
            image_height: int
    ) -> float:
        """Вычисляет риск (размер 40%, уверенность 30%, позиция 30%)"""
        size_ratio = (box_area / image_area) * 100
        size_score = min(size_ratio * 5, 100)
        conf_score = confidence * 100
        center_distance = abs((position_y / image_height) - 0.5) * 2
        position_score = (1 - center_distance) * 100
        total_risk = (size_score * 0.4 + conf_score * 0.3 + position_score * 0.3)
        return total_risk

    @staticmethod
    def classify_pothole_severity(
            box_area: float,
            image_area: float,
            confidence: float,
            position_y: int,
            image_height: int
    ) -> Tuple[str, Tuple, str, float]:
        """Классификация с учётом риска"""
        risk_score = PotholeDetectionService.calculate_pothole_risk_score(
            box_area, image_area, confidence, position_y, image_height
        )

        if risk_score > 70:
            severity = 'CRITICAL'
            color_bgr = (0, 0, 200)
            label_text = 'КРИТИЧЕСКИЙ'
        elif risk_score > 50:
            severity = 'HIGH'
            color_bgr = (0, 0, 255)
            label_text = 'ОПАСНЫЙ'
        elif risk_score > 30:
            severity = 'MEDIUM'
            color_bgr = (0, 165, 255)
            label_text = 'СРЕДНИЙ'
        else:
            severity = 'LOW'
            color_bgr = (0, 255, 0)
            label_text = 'НИЗКИЙ'

        return severity, color_bgr, label_text, risk_score

    def _process_image_sync(self, image_bytes: bytes) -> Tuple[bytes, Dict, List]:
        """Синхронная обработка изображения с YOLO11"""
        if self.model is None:
            raise HTTPException(status_code=500, detail="YOLO11 модель не загружена")

        # Декодирование изображения
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Ошибка при загрузке изображения")

        orig_h, orig_w = image.shape[:2]
        image_area = orig_h * orig_w


        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            imgsz=self.imgsz,
            verbose=False,
            augment=False,
            agnostic_nms=True
        )[0]

        output_image = image.copy()
        img_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_image)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                except:
                    font = ImageFont.load_default()

        severity_stats = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        all_risks = []


        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
            confidences = results.boxes.conf.cpu().numpy()

            for box, conf in zip(boxes, confidences):
                x1, y1, x2, y2 = map(int, box)

                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(orig_w, x2)
                y2 = min(orig_h, y2)

                box_area = (x2 - x1) * (y2 - y1)
                center_y = (y1 + y2) // 2

                severity, color_bgr, label_text, risk_score = self.classify_pothole_severity(
                    box_area, image_area, float(conf), center_y, orig_h
                )

                severity_stats[severity] += 1
                all_risks.append(risk_score)

                color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])

                box_width = 4 if risk_score > 50 else 2
                draw.rectangle([x1, y1, x2, y2], outline=color_rgb, width=box_width)

                label = f"{label_text} {risk_score:.0f}% (conf: {conf:.2f})"
                bbox = draw.textbbox((x1, y1 - 25), label, font=font)
                draw.rectangle(bbox, fill=color_rgb)
                draw.text((x1, y1 - 25), label, fill=(0, 0, 0), font=font)

        output_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', output_image, [cv2.IMWRITE_JPEG_QUALITY, 90])

        return buffer.tobytes(), severity_stats, all_risks

    async def process_single_image(
            self,
            image_bytes: bytes,
            input_data: InputValues,
            filename: str,
            db: AsyncSession
    ) -> DetectionResponse:
        """Обработка одного изображения"""
        try:
            result_bytes, stats, risks = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._process_image_sync, image_bytes
            )
            image_url = await self.s3_service.upload_file(
                file_bytes=result_bytes,
                folder="processed/images",
                filename=filename,
                content_type="image/jpeg"
            )
            address = await self.geocoding_service.geocode_coordinates(
                latitude=input_data.latitude,
                longitude=input_data.longitude
            )

            return DetectionResponse(
                user_id = input_data.user_id,
                filename=filename,
                detections=SeverityStats(**stats),
                average_risk=float(np.mean(risks)) if risks else 0.0,
                max_risk=float(np.max(risks)) if risks else 0.0,
                total_potholes=sum(stats.values()),
                image_url=image_url,
                address=address,
                latitude=input_data.latitude,
                longitude=input_data.longitude
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

    async def process_multiple_images_bytes(
            self,
            images_data: List[Tuple[bytes, str]],
            input_data,
            db: AsyncSession
    ) -> MultipleDetectionResponse:
        """Обработка нескольких изображений из base64 с загрузкой в S3"""
        results = []
        successful = 0
        failed = 0

        tasks = []
        for idx, (image_bytes, filename) in enumerate(images_data):
            task = self._process_single_image_task(
                image_bytes, filename, idx, input_data
            )
            tasks.append(task)

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in task_results:
            if isinstance(result, Exception):
                results.append(SingleImageResult(
                    filename="unknown",
                    index=len(results),
                    detections=SeverityStats(),
                    average_risk=0.0,
                    max_risk=0.0,
                    total_potholes=0,
                    error=str(result)
                ))
                failed += 1
            else:
                results.append(result)
                if result.error is None:
                    successful += 1
                else:
                    failed += 1

        address = await self.geocoding_service.geocode_coordinates(
            latitude=input_data.latitude,
            longitude=input_data.longitude
        )

        return MultipleDetectionResponse(
            user_id = input_data.user_id,
            total_images=len(images_data),
            successful=successful,
            failed=failed,
            results=results,
            address=address,
            latitude=input_data.latitude,
            longitude=input_data.longitude
        )

    async def _process_single_image_task(
            self,
            image_bytes: bytes,
            filename: str,
            idx: int,
            input_data
    ) -> SingleImageResult:
        """Задача для обработки одного изображения"""
        try:
            result_bytes, stats, risks = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._process_image_sync, image_bytes
            )

            image_url = await self.s3_service.upload_file(
                file_bytes=result_bytes,
                folder="processed/images",
                filename=filename,
                content_type="image/jpeg"
            )

            return SingleImageResult(
                filename=filename,
                index=idx,
                detections=SeverityStats(**stats),
                average_risk=float(np.mean(risks)) if risks else 0.0,
                max_risk=float(np.max(risks)) if risks else 0.0,
                total_potholes=sum(stats.values()),
                image_url=image_url
            )
        except Exception as e:
            return SingleImageResult(
                filename=filename,
                index=idx,
                detections=SeverityStats(),
                average_risk=0.0,
                max_risk=0.0,
                total_potholes=0,
                error=str(e)
            )

    async def process_video_bytes(
            self,
            video_bytes: bytes,
            input_data,
            filename: str,
            db: AsyncSession
    ) -> VideoDetectionResponse:
        """Обработка видео из base64 с загрузкой в S3"""
        if self.model is None:
            raise HTTPException(status_code=500, detail="YOLO11 модель не загружена")

        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4', mode='wb')
        temp_input.write(video_bytes)
        temp_input.close()

        try:
            cap = cv2.VideoCapture(temp_input.name)
            if not cap.isOpened():
                raise HTTPException(status_code=400, detail="Не удалось открыть видео")

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_output.close()

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_output.name, fourcc, fps, (width, height))

            frame_count = 0
            all_stats = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            all_risks_combined = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                try:
                    result_bytes, stats, risks = await asyncio.get_event_loop().run_in_executor(
                        self.executor, self._process_image_sync, frame_bytes
                    )

                    processed_frame = cv2.imdecode(
                        np.frombuffer(result_bytes, np.uint8),
                        cv2.IMREAD_COLOR
                    )

                    out.write(processed_frame)

                    for key in all_stats:
                        all_stats[key] += stats[key]

                    all_risks_combined.extend(risks)

                except Exception as e:
                    out.write(frame)

                frame_count += 1

            cap.release()
            out.release()

            with open(temp_output.name, 'rb') as video_file:
                processed_video_bytes = video_file.read()

            video_url = await self.s3_service.upload_file(
                file_bytes=processed_video_bytes,
                folder="processed/videos",
                filename=filename,
                content_type="video/mp4"
            )

            address = await self.geocoding_service.geocode_coordinates(
                latitude=input_data.latitude,
                longitude=input_data.longitude
            )

            return VideoDetectionResponse(
                filename=filename,
                total_frames=total_frames,
                processed_frames=frame_count,
                detections=SeverityStats(**all_stats),
                average_risk=float(np.mean(all_risks_combined)) if all_risks_combined else 0.0,
                max_risk=float(np.max(all_risks_combined)) if all_risks_combined else 0.0,
                duration_seconds=total_frames / fps if fps > 0 else 0.0,
                video_url=video_url,
                address=address,
                latitude=input_data.latitude,
                longitude=input_data.longitude
            )

        finally:
            try:
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)
            except:
                pass
