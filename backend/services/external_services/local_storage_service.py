from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from uuid import uuid4

import aiofiles


MEDIA_ROOT = Path(__file__).resolve().parents[2] / "media"
MEDIA_URL_PREFIX = "/media"


class LocalStorageService:
    def __init__(self, media_root: Path = MEDIA_ROOT):
        self.media_root = media_root.resolve()
        self.media_root.mkdir(parents=True, exist_ok=True)

    async def upload_file(
            self,
            file_bytes: bytes,
            folder: str = "processed",
            filename: Optional[str] = None,
            content_type: str = "image/jpeg",
            base_url: str = ""
    ) -> str:
        folder_path = self._safe_folder(folder)
        safe_filename = self._build_filename(filename, content_type)
        destination = folder_path / safe_filename

        async with aiofiles.open(destination, "wb") as file:
            await file.write(file_bytes)

        relative_path = destination.relative_to(self.media_root).as_posix()
        return f"{base_url.rstrip('/')}{MEDIA_URL_PREFIX}/{relative_path}"

    async def read_file(self, file_url: str) -> Optional[bytes]:
        try:
            path = self._resolve_file_url(file_url)
            if not path.is_file():
                return None
            async with aiofiles.open(path, "rb") as file:
                return await file.read()
        except (OSError, ValueError):
            return None

    async def delete_file(self, file_url: str) -> bool:
        try:
            self._resolve_file_url(file_url).unlink(missing_ok=True)
            return True
        except (OSError, ValueError):
            return False

    async def list_files(self, prefix: str = "") -> list[str]:
        folder = self._safe_folder(prefix)
        return [path.relative_to(self.media_root).as_posix() for path in folder.rglob("*") if path.is_file()]

    def _resolve_file_url(self, file_url: str) -> Path:
        url_path = urlparse(file_url).path
        prefix = f"{MEDIA_URL_PREFIX}/"
        if not url_path.startswith(prefix):
            raise ValueError("URL не относится к локальному хранилищу")
        path = (self.media_root / url_path.removeprefix(prefix)).resolve()
        path.relative_to(self.media_root)
        return path

    def _safe_folder(self, folder: str) -> Path:
        parts = [part for part in Path(folder).parts if part not in {"", ".", "..", "/", "\\"}]
        path = self.media_root.joinpath(*parts).resolve()
        path.relative_to(self.media_root)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _build_filename(filename: Optional[str], content_type: str) -> str:
        extension = Path(filename).suffix.lower() if filename else ""
        if not extension:
            extension = ".jpg" if content_type.startswith("image/") else ".mp4"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{uuid4().hex[:12]}{extension}"
