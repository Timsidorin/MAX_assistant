import aioboto3
import asyncio
from typing import Optional
from datetime import datetime
import uuid
from io import BytesIO

from backend.core.config import configs


class S3Service:
    """Сервис для работы с S3"""

    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=configs.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=configs.AWS_SECRET_ACCESS_KEY,
            region_name=configs.S3_REGION_NAME
        )
        self.bucket_name = configs.S3_BUCKET_NAME
        self.endpoint_url = configs.S3_ENDPOINT_URL

    async def upload_file(
            self,
            file_bytes: bytes,
            folder: str = "processed",
            filename: Optional[str] = None,
            content_type: str = "image/jpeg"
    ) -> str:
        """
        Загрузка файла в S3

        Args:
            file_bytes: Байты файла
            folder: Папка в S3 (processed, videos, etc.)
            filename: Имя файла (если None, генерируется автоматически)
            content_type: MIME-тип файла

        Returns:
            URL загруженного файла
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            ext = "jpg" if "image" in content_type else "mp4"
            filename = f"{timestamp}_{unique_id}.{ext}"

        s3_key = f"{folder}/{filename}"

        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url
        ) as s3:
            try:
                file_obj = BytesIO(file_bytes)

                await s3.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'ACL': 'public-read'
                    }
                )

                # Формируем URL
                if self.endpoint_url:
                    file_url = f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"
                else:
                    file_url = f"https://{self.bucket_name}.s3.{configs.S3_REGION_NAME}.amazonaws.com/{s3_key}"

                return file_url

            except Exception as e:
                print(f"❌ Ошибка загрузки в S3: {e}")
                raise

    async def delete_file(self, s3_key: str) -> bool:
        """
        Удаление файла из S3

        Args:
            s3_key: Ключ файла в S3

        Returns:
            True если успешно удалено
        """
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                return True
            except Exception as e:
                print(f"❌ Ошибка удаления из S3: {e}")
                return False

    async def check_bucket_exists(self) -> bool:
        """Проверка существования bucket"""
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket_name)
                return True
            except:
                return False

    async def create_bucket_if_not_exists(self):
        """Создание bucket если не существует"""
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url
        ) as s3:
            try:
                if not await self.check_bucket_exists():
                    await s3.create_bucket(Bucket=self.bucket_name)
                    print(f"✅ Bucket {self.bucket_name} создан")
            except Exception as e:
                print(f"❌ Ошибка создания bucket: {e}")
