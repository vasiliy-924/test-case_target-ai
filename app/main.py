from fastapi import FastAPI

from config import get_app_port, get_redis_url
from ws import router as ws_router

app = FastAPI()

app.include_router(ws_router)


@app.get("/")
def root():
    return {"message": "WebSocket Service is running"}


@app.get("/config")
def get_config():
    return {
        "APP_PORT": get_app_port(),
        "REDIS_URL": get_redis_url()
    }
