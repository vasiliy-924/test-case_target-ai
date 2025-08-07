import os
from typing import Optional

from dotenv import load_dotenv

from constants import DEFAULT_MAX_AUDIO_SIZE_BYTES

# Загружаем переменные из .env
load_dotenv()

APP_PORT = int(os.getenv("APP_PORT", 8000))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
MAX_AUDIO_SIZE = int(
    os.getenv("MAX_AUDIO_SIZE", DEFAULT_MAX_AUDIO_SIZE_BYTES)
)


def get_app_port() -> int:
    return APP_PORT


def get_redis_url() -> str:
    return REDIS_URL


def get_max_audio_size() -> int:
    return MAX_AUDIO_SIZE
