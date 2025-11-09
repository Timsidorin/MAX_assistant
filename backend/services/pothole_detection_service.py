import cv2
import numpy as np
import onnxruntime as ort
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
from backend.services.external_services.geo_service import  GeocodingService
from backend.services.external_services.s3_service import S3Service


class PotholeDetectionService:
    """Сервис для детекции ям на дорожном покрытии"""

    def __init__(self, model_path: str = './cv_models/best.onnx', max_workers: int = 4):
        self.model_path = model_path
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.session = self._load_model()
        self.s3_service = S3Service()
        self.geocoding_service = GeocodingService()

    def _load_model(self):
        """Загрузка ONNX модели"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Модель не найдена: {self.model_path}")

            providers = ['CPUExecutionProvider']
            session = ort.InferenceSession(self.model_path, providers=providers)
            return session
        except Exception as e:
            print(f"Ошибка загрузки ONNX: {e}")
            return None

    def is_model_loaded(self) -> bool:
        """Проверка загрузки модели"""
        return self.session is not None

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

    @staticmethod
    def preprocess_image(img: np.ndarray, target_size: int = 640):
        """Подготовка изображения"""
        h, w = img.shape[:2]
        scale = min(target_size / w, target_size / h)
        new_w, new_h = int(w * scale), int(h * scale)

        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        canvas = np.full((target_size, target_size, 3), 114, dtype=np.uint8)
        dw = (target_size - new_w) // 2
        dh = (target_size - new_h) // 2
        canvas[dh:dh + new_h, dw:dw + new_w] = resized

        img_norm = canvas.astype(np.float32) / 255.0
        img_tensor = np.transpose(img_norm, (2, 0, 1))
        img_tensor = np.expand_dims(img_tensor, 0)

        return img_tensor, scale, dw, dh

    @staticmethod
    def postprocess_detections(outputs, conf_thresh: float = 0.25, iou_thresh: float = 0.45):
        """Обработка выходов модели"""
        detections = []
        pred = outputs[0][0]

        conf_mask = pred[:, 4] > conf_thresh
        pred = pred[conf_mask]

        if len(pred) == 0:
            return detections

        boxes = pred[:, :4]
        confs = pred[:, 4]

        boxes_xyxy = np.concatenate([
            boxes[:, :2] - boxes[:, 2:] / 2,
            boxes[:, :2] + boxes[:, 2:] / 2
        ], axis=1)

        keep = []
        order = np.argsort(confs)[::-1]

        for i in order:
            if len(keep) == 0:
                keep.append(i)
            else:
                x1_i, y1_i, x2_i, y2_i = boxes_xyxy[i]
                skip = False

                for j in keep:
                    x1_j, y1_j, x2_j, y2_j = boxes_xyxy[j]

                    xi1 = max(x1_i, x1_j)
                    yi1 = max(y1_i, y1_j)
                    xi2 = min(x2_i, x2_j)
                    yi2 = min(y2_i, y2_j)

                    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)

                    area_i = (x2_i - x1_i) * (y2_i - y1_i)
                    area_j = (x2_j - x1_j) * (y2_j - y1_j)
                    union = area_i + area_j - inter

                    iou = inter / union if union > 0 else 0

                    if iou > iou_thresh:
                        skip = True
                        break

                if not skip:
                    keep.append(i)

        for idx in keep:
            detections.append({
                'box': boxes_xyxy[idx],
                'conf': confs[idx]
            })

        return detections

    def _process_image_sync(self, image_bytes: bytes) -> Tuple[bytes, Dict, List]:
        """Синхронная обработка изображения (CV логика)"""
        if self.session is None:
            raise HTTPException(status_code=500, detail="ONNX модель не загружена")

        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Ошибка при загрузке изображения")

        orig_h, orig_w = image.shape[:2]
        image_area = orig_h * orig_w

        img_tensor, scale, dw, dh = self.preprocess_image(image)

        input_name = self.session.get_inputs()[0].name
        output_names = [o.name for o in self.session.get_outputs()]

        outputs = self.session.run(output_names, {input_name: img_tensor})
        detections = self.postprocess_detections(outputs, conf_thresh=0.25, iou_thresh=0.45)

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

        for det in detections:
            x1, y1, x2, y2 = det['box'].astype(int)
            conf = det['conf']

            x1 = int((x1 - dw) / scale)
            y1 = int((y1 - dh) / scale)
            x2 = int((x2 - dw) / scale)
            y2 = int((y2 - dh) / scale)

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(orig_w, x2)
            y2 = min(orig_h, y2)

            box_area = (x2 - x1) * (y2 - y1)
            center_y = (y1 + y2) // 2

            severity, color_bgr, label_text, risk_score = self.classify_pothole_severity(
                box_area, image_area, conf, center_y, orig_h
            )

            severity_stats[severity] += 1
            all_risks.append(risk_score)

            color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])

            box_width = 4 if risk_score > 50 else 2
            draw.rectangle([x1, y1, x2, y2], outline=color_rgb, width=box_width)

            label = f"{label_text} {risk_score:.0f}%"
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
        """
        Обработка одного изображения

        Процесс:
        1. Получить сырое фото (из base64)
        2. Обработать его (детекция)
        3. Загрузить в S3
        4. Получить адрес по координатам
        5. Вернуть URL и адрес
        """
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

        # Создаем задачи для параллельной обработки
        tasks = []
        for idx, (image_bytes, filename) in enumerate(images_data):
            task = self._process_single_image_task(
                image_bytes, filename, idx, input_data
            )
            tasks.append(task)

        # Выполняем все задачи параллельно
        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Собираем результаты
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

        print(f"🌍 Запрашиваем адрес для координат: {input_data.latitude}, {input_data.longitude}")
        address = await self.geocoding_service.geocode_coordinates(
            latitude=input_data.latitude,
            longitude=input_data.longitude
        )
        print(f"📍 Получен адрес: {address}")

        return MultipleDetectionResponse(
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
            # Обрабатываем
            result_bytes, stats, risks = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._process_image_sync, image_bytes
            )

            # Загружаем в S3
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
        if self.session is None:
            raise HTTPException(status_code=500, detail="ONNX модель не загружена")

        # Сохраняем входное видео во временный файл
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

            # Создаем выходное видео
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_output.close()

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_output.name, fourcc, fps, (width, height))

            frame_count = 0
            all_stats = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            all_risks_combined = []

            print(f"🎬 Начало обработки видео: {total_frames} фреймов")

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
                    print(f"⚠️ Ошибка обработки фрейма {frame_count}: {e}")
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
            # Очистка временных файлов
            try:
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)
            except:
                pass
