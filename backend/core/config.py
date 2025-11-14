from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, ClassVar, Dict, Any
import os


class Configs(BaseSettings):
    """Главный конфиг проекта"""
    # ------------ Настройки проекта ------------
    PROJECT_NAME: str = "Ассистент по дорожным обращениям"

    # ------------ Пользовательсвие уровни ------------
    USER_LEVELS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"name": "👶 Начинающий ямоборец", "points": 0},
        2: {"name": "🚶  ямоборец-активист", "points": 100},
        3: {"name": "🚗 Водитель-жалобщик", "points": 300},
        4: {"name": "🔍 Инспектор дорог", "points": 600},
        5: {"name": "🏆 Мастер ямоборения", "points": 1000},
        6: {"name": "🌟 Легенда городских дорог", "points": 2000}
    }

    # ------------ Веб-сервер ------------
    HOST: str = "localhost"
    PORT: int = 8005

    # ------------ БД ------------
    DB_HOST: Optional[str] = Field(default="localhost", env="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, env="DB_PORT")
    DB_USER: Optional[str] = Field(default="admin", env="DB_USER")
    DB_NAME: Optional[str] = Field(default="MAX", env="DB_NAME")
    DB_PASS: Optional[str] = Field(default="admin", env="DB_PASS")

    # ------------ Почта (оповещение) ------------
    MAILRU_SMTP_HOST: Optional[str] = Field(default="smtp.mail.ru", env="MAILRU_SMTP_HOST")
    MAILRU_SMTP_PORT: Optional[int] = Field(default=465, env="MAILRU_SMTP_PORT")
    MAILRU_SMTP_USER: Optional[str] = Field(default="MAILRU_SMTP_USER", env="MAILRU_SMTP_USER")
    MAILRU_SMTP_PASSWORD: Optional[str] = Field(default="MAILRU_SMTP_PASSWORD", env="MAILRU_SMTP_PASSWORD")



    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default="AWS_ACCESS_KEY_ID", env="AWS_ACCESS_KEY_ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default="AWS_SECRET_ACCESS_KEY", env="AWS_SECRET_ACCESS_KEY"
    )
    S3_BUCKET_NAME: Optional[str] = Field(
        default="S3_BUCKET_NAME", env="S3_BUCKET_NAME"
    )
    S3_ENDPOINT_URL: Optional[str] = Field(
        default="https://hb.ru-msk.S3_ENDPOINT_URL-storage.ru/", env="S3_ENDPOINT_URL"
    )
    S3_REGION_NAME: Optional[str] = Field(default="ru-msk", env="S3_REGION_NAME")


    model_config = SettingsConfigDict(
        env_file="../../.env"
    )


configs = Configs()

def get_db_url():
    return (
        f"postgresql+asyncpg://{configs.DB_USER}:{configs.DB_PASS}@"
        f"{configs.DB_HOST}:{configs.DB_PORT}/{configs.DB_NAME}"
    )


def get_auth_data():
    return {"secret_key": configs.SECRET_KEY, "algorithm": configs.ALGORITHM}

