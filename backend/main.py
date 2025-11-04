"""
Точка входа в backend
"""

#


from fastapi import FastAPI, APIRouter
from core.config import configs
from core.create_base_app import create_base_app


app = create_base_app(configs)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)


