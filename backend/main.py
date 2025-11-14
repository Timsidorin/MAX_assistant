"""
Точка входа в backend
"""
import logging
from urllib.request import Request

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse

from backend.core.config import configs
from backend.core.create_base_app import create_base_app
from backend.models.users_model import User
from backend.models.report_model import ReportStatus, ReportPriority
from backend.routers.cv_router import cv_router
from backend.routers.reports_router import report_router
from backend.routers.users_router import users_router
from routers.tasks_router import tasks_router

app = create_base_app(configs)


app.include_router(router=cv_router)
app.include_router(router=report_router)
app.include_router(router=users_router)
app.include_router(router=tasks_router)



logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик для всех непойманных исключений"""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже.",
            "type": "internal_error"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик для ошибок валидации Pydantic"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "type": "validation_error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)
