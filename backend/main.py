"""
Точка входа в backend
"""

from fastapi import FastAPI, APIRouter

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)
