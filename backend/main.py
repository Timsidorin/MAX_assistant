"""
Точка входа в backend
"""

#


from fastapi import FastAPI, APIRouter

from backend.routers.cv_router import cv_router
from core.config import configs
from core.create_base_app import create_base_app


app = create_base_app(configs)

app.include_router(router=cv_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)


