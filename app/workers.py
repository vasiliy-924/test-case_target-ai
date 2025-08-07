import asyncio
import base64
import json
import logging
from datetime import datetime

from redis_client import get_redis_client
from constants import AUDIO_CHANNEL, TRANSCRIPTS_CHANNEL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def mock_transcribe_audio(audio_data: bytes) -> str:
    """Возвращает mock-транскрипт с текущей меткой времени."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_size = len(audio_data)
    return f"Transcribed: {timestamp} (size: {data_size} bytes)"


async def process_audio_chunks():
    """Подписывается на audio_chunks, генерирует и публикует транскрипты."""
    logger.info("Starting audio processing worker...")

    redis = None
    pubsub = None
    try:
        redis = await get_redis_client()
        pubsub = redis.pubsub()

        # Подписываемся на канал audio_chunks
        await pubsub.subscribe(AUDIO_CHANNEL)
        logger.info(f"Subscribed to channel: {AUDIO_CHANNEL}")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
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

                    await redis.publish(
                        TRANSCRIPTS_CHANNEL,
                        json.dumps({"client_id": client_id,
                                   "text": transcript}).encode("utf-8")
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
            if pubsub is not None:
                await pubsub.unsubscribe(AUDIO_CHANNEL)
                await pubsub.close()
            if redis is not None:
                await redis.close()
            logger.info("Worker stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Точка входа воркера с автоперезапуском при ошибках."""
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
