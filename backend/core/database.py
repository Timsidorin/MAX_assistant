from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncAttrs,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData
import asyncio
from backend.core.config import get_db_url
from typing import AsyncGenerator

DATABASE_URL = get_db_url()

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий БД для dependency injection"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
