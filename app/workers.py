import asyncio
import logging
from datetime import datetime
import json
import base64

from redis_client import (
    get_redis_client,
    AUDIO_CHANNEL,
    TRANSCRIPTS_CHANNEL
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def mock_transcribe_audio(audio_data: bytes) -> str:
    """
    Создает фиктивный транскрипт для аудио данных.

    Args:
        audio_data (bytes): Бинарные аудио данные

    Returns:
        str: Фиктивный транскрипт с временной меткой
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_size = len(audio_data)
    return f"Transcribed: {timestamp} (size: {data_size} bytes)"


async def process_audio_chunks():
    """
    Основная функция воркера для обработки аудио чанков.
    Подписывается на канал audio_chunks и публикует транскрипты.
    """
    logger.info("Starting audio processing worker...")

    try:
        redis = await get_redis_client()
        pubsub = redis.pubsub()

        # Подписываемся на канал audio_chunks
        await pubsub.subscribe(AUDIO_CHANNEL)
        logger.info(f"Subscribed to channel: {AUDIO_CHANNEL}")

        # Обрабатываем сообщения
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    # Декодируем JSON
                    payload = json.loads(message["data"].decode("utf-8"))
                    client_id = payload["client_id"]
                    audio_data = base64.b64decode(payload["audio"])
                    logger.info(
                        f"Received audio chunk from client {client_id}: {len(audio_data)} bytes"
                    )

                    # Создаем фиктивный транскрипт
                    transcript = await mock_transcribe_audio(audio_data)
                    logger.info(
                        f"Generated transcript: {transcript} for client {client_id}"
                    )

                    # Публикуем транскрипт в канал transcripts как JSON
                    await redis.publish(
                        TRANSCRIPTS_CHANNEL,
                        json.dumps({"client_id": client_id, "text": transcript}).encode("utf-8")
                    )
                    logger.info(
                        f"Published transcript to channel: {TRANSCRIPTS_CHANNEL} for client {client_id}"
                    )

                except Exception as e:
                    logger.error(f"Error processing audio chunk: {e}")

    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise
    finally:
        try:
            await pubsub.unsubscribe(AUDIO_CHANNEL)
            await pubsub.close()
            await redis.close()
            logger.info("Worker stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """
    Главная функция для запуска воркера.
    """
    logger.info("Starting mock transcription worker...")

    while True:
        try:
            await process_audio_chunks()
        except Exception as e:
            logger.error(f"Worker crashed: {e}")
            logger.info("Restarting worker in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
