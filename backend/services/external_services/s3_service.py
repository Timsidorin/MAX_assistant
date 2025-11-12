import aioboto3
from botocore.config import Config
from typing import Optional
from datetime import datetime
import uuid
from io import BytesIO

from backend.core.config import configs


class S3Service:
    """Сервис для работы с S3"""

    def __init__(self):
        self.config = Config(
            s3={'addressing_style': 'virtual'},
            request_checksum_calculation="when_required",
            response_checksum_validation=None
        )

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
                endpoint_url=self.endpoint_url,
                config=self.config
        ) as s3:
            try:
                file_obj = BytesIO(file_bytes)

                await s3.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type
                    }
                )
                await s3.put_object_acl(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    ACL='public-read'
                )
                file_url = f"https://{self.bucket_name}.hb.ru-msk.vkcloud-storage.ru/{s3_key}"
                return file_url

            except Exception as e:
                print(f"Ошибка загрузки в S3: {e}")
                raise

    async def delete_file(self, s3_key: str) -> bool:
        """
        Удаление файла из S3
        Returns:
            True если успешно удалено
        """
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                config=self.config
        ) as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                return True
            except Exception as e:
                return False

    async def check_bucket_exists(self) -> bool:
        """Проверка существования bucket"""
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                config=self.config
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
                endpoint_url=self.endpoint_url,
                config=self.config
        ) as s3:
            try:
                if not await self.check_bucket_exists():
                    await s3.create_bucket(Bucket=self.bucket_name)
                    print(f"Bucket {self.bucket_name} создан")
            except Exception as e:
                print(f"Ошибка создания bucket: {e}")

    async def make_bucket_public(self):
        """
        Делает весь bucket публичным (опционально)
        """
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                config=self.config
        ) as s3:
            try:
                await s3.put_bucket_acl(
                    Bucket=self.bucket_name,
                    ACL='public-read'
                )
            except Exception as e:
                print(f"❌ Ошибка настройки ACL bucket: {e}")

    async def list_files(self, prefix: str = "") -> list:
        """
        Получить список файлов в bucket

        Returns:
            Список ключей файлов
        """
        async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                config=self.config
        ) as s3:
            try:
                response = await s3.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )

                if 'Contents' in response:
                    return [obj['Key'] for obj in response['Contents']]
                return []
            except Exception as e:
                print(f"Ошибка получения списка файлов: {e}")
                return []
