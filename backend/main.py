"""
Точка входа в backend
"""

from fastapi import FastAPI, APIRouter

from backend.models.users_model import User
from backend.models.report_model import ReportStatus, ReportPriority


from backend.routers.cv_router import cv_router
from backend.routers.reports_router import report_router
from core.config import configs
from core.create_base_app import create_base_app



app = create_base_app(configs)


app.include_router(router=cv_router)
app.include_router(router=report_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)
