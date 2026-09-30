from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, ClassVar, Dict, Any
import os


class Configs(BaseSettings):
    """Главный конфиг проекта"""
    PROJECT_NAME: str = "Ассистент по дорожным обращениям"

    USER_LEVELS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"name": "👶 Начинающий ямоборец", "points": 0},
        2: {"name": "🚶  ямоборец-активист", "points": 100},
        3: {"name": "🚗 Водитель-жалобщик", "points": 300},
        4: {"name": "🔍 Инспектор дорог", "points": 600},
        5: {"name": "🏆 Мастер ямоборения", "points": 1000},
        6: {"name": "🌟 Легенда городских дорог", "points": 2000}
    }

    HOST: str = "localhost"
    PORT: int = 8005

    DB_HOST: Optional[str] = Field(default="localhost", env="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, env="DB_PORT")
    DB_USER: Optional[str] = Field(default="admin", env="DB_USER")
    DB_NAME: Optional[str] = Field(default="MAX", env="DB_NAME")
    DB_PASS: Optional[str] = Field(default="admin", env="DB_PASS")

    YANDEX_SMTP_HOST: str = Field(default="smtp.yandex.ru", env="YANDEX_SMTP_HOST")
    YANDEX_SMTP_PORT: int = Field(default=465, env="YANDEX_SMTP_PORT")
    YANDEX_SMTP_USER: str = Field(default="", env="YANDEX_SMTP_USER")
    YANDEX_SMTP_PASSWORD: str = Field(default="", env="YANDEX_SMTP_PASSWORD")
    EMAIL_FROM_NAME: str = Field(default="Ямоборец", env="EMAIL_FROM_NAME")


    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")),
        extra="ignore",
    )


configs = Configs()

def get_db_url():
    return (
        f"postgresql+asyncpg://{configs.DB_USER}:{configs.DB_PASS}@"
        f"{configs.DB_HOST}:{configs.DB_PORT}/{configs.DB_NAME}"
    )

