from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Configs(BaseSettings):
    """Главный конфиг проекта"""
    # ------------ Настройки проекта ------------
    PROJECT_NAME: str = "Ассистент по дорожным обращениям"

    # ------------ Веб-сервер ------------
    HOST: str = "localhost"
    PORT: int = 8005

    # ------------ БД ------------
    DB_HOST: Optional[str] = Field(default="localhost", env="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, env="DB_PORT")
    DB_USER: Optional[str] = Field(default="postgres", env="DB_USER")
    DB_NAME: Optional[str] = Field(default="MAX", env="DB_NAME")
    DB_PASS: Optional[str] = Field(default="admin", env="DB_PASS")

    # ------------ Почта (оповещение) ------------
    MAIL_USERNAME: Optional[str] = Field(
        default="timsidorin@gmail.com", env="MAIL_USERNAME"
    )
    MAIL_PASSWORD: Optional[str] = Field(
        default="xdfj qlia vmpy gskl", env="MAIL_PASSWORD"
    )
    MAIL_FROM: Optional[str] = Field(default="timsidorin@gmail.com", env="MAIL_FROM")
    MAIL_PORT: Optional[int] = Field(default=587, env="MAIL_PORT")
    MAIL_SERVER: Optional[str] = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    MAIL_STARTTLS: bool = Field(default=True, env="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, env="MAIL_SSL_TLS")



    # ------------ S3 хранилище ----------------------------------------
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default="PBZ2LEBQ3L0Q9PE7N7YY", env="AWS_ACCESS_KEY_ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default="QAjuuUc2Xwwq7rggsNnvXNcnywwXWQ3tNSRS1FNi", env="AWS_SECRET_ACCESS_KEY"
    )
    S3_BUCKET_NAME: Optional[str] = Field(
        default="ec4f5e2a-70163ded-082f-4975-95f1-f0b1bf534bf0", env="S3_BUCKET_NAME"
    )
    S3_ENDPOINT_URL: Optional[str] = Field(
        default="https://s3.twcstorage.ru", env="S3_ENDPOINT_URL"
    )
    S3_REGION_NAME: Optional[str] = Field(default="ru-1", env="S3_REGION_NAME")


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


configs = Configs()

def get_db_url():
    return (
        f"postgresql+asyncpg://{configs.DB_USER}:{configs.DB_PASS}@"
        f"{configs.DB_HOST}:{configs.DB_PORT}/{configs.DB_NAME}"
    )


def get_auth_data():
    return {"secret_key": configs.SECRET_KEY, "algorithm": configs.ALGORITHM}
