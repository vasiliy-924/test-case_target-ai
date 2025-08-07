import redis.asyncio as redis

from config import get_redis_url
from constants import AUDIO_CHANNEL, TRANSCRIPTS_CHANNEL


async def get_redis_client():
    """Создает и возвращает асинхронный клиент Redis (redis.asyncio)."""
    return redis.from_url(get_redis_url(), decode_responses=False)


async def test_redis_connection():
    """Проверяет доступность Redis командой PING."""
    try:
        redis = await get_redis_client()
        result = await redis.ping()
        await redis.close()
        return bool(result) or result == b"PONG"
    except Exception as e:
        print(f"Redis connection test failed: {e}")
        return False


async def publish_audio_chunk(data: bytes):
    """Публикует бинарный аудио-чанк в канал Redis."""
    redis = await get_redis_client()
    try:
        await redis.publish(AUDIO_CHANNEL, data)
    finally:
        await redis.close()


async def subscribe_to_transcripts(callback):
    """Подписывается на канал транскриптов и вызывает callback на каждое сообщение."""
    redis = await get_redis_client()
    pubsub = redis.pubsub()
    try:
        await pubsub.subscribe(TRANSCRIPTS_CHANNEL)
        async for message in pubsub.listen():
            if message["type"] == "message":
                text = message["data"].decode("utf-8", errors="ignore")
                await callback(text)
    except Exception as e:
        print(f"Error in transcript subscription: {e}")
    finally:
        await pubsub.unsubscribe(TRANSCRIPTS_CHANNEL)
        await pubsub.close()
        await redis.close()
