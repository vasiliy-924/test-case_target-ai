import os

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

APP_PORT = int(os.getenv("APP_PORT", 8000))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def get_app_port() -> int:
    return APP_PORT


def get_redis_url() -> str:
    return REDIS_URL
