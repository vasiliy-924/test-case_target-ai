import asyncio
import base64
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from redis_client import get_redis_client
from constants import AUDIO_CHANNEL, TRANSCRIPTS_CHANNEL
from config import get_max_audio_size

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()


def validate_audio_data(data: bytes) -> tuple[bool, Optional[str]]:
    """Проверяет аудио-данные: не пустые и не превышают лимит размера."""
    if not data:
        return False, "Audio data is empty"

    max_size = get_max_audio_size()
    if len(data) > max_size:
        return False, f"Audio data too large (max {max_size} bytes)"

    return True, None


def validate_transcript_data(data: bytes) -> tuple[bool, Optional[str]]:
    """Проверяет транскрипт: валидная UTF-8 и непустой текст."""
    if not data:
        return False, "Transcript data is empty"

    try:
        text = data.decode("utf-8")
        if not text.strip():
            return False, "Transcript text is empty"
        return True, None
    except UnicodeDecodeError:
        return False, "Invalid transcript encoding"


async def send_error_response(websocket: WebSocket, error_message: str):
    """Отправляет клиенту JSON с ошибкой через WebSocket."""
    try:
        await websocket.send_json({
            "error": error_message,
            "status": "error"
        })
        logger.error(f"Sent error to client: {error_message}")
    except Exception as e:
        logger.error(f"Failed to send error response: {e}")


async def listen_transcripts(redis, websocket, client_id):
    """Слушает Redis-канал транскриптов и ретранслирует сообщения клиенту."""
    pubsub = redis.pubsub()
    await pubsub.subscribe(TRANSCRIPTS_CHANNEL)
    logger.info(f"Client {client_id} subscribed to transcripts channel")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    # Валидируем данные транскрипта
                    is_valid, error_msg = validate_transcript_data(
                        message["data"])
                    if not is_valid:
                        logger.error(f"Invalid transcript data: {error_msg}")
                        await send_error_response(
                            websocket, error_msg or "Invalid transcript data"
                        )
                        continue

                    # Декодируем JSON транскрипта
                    transcript_data = json.loads(message["data"].decode("utf-8"))
                    if transcript_data.get("client_id") != client_id:
                        continue
                    text = transcript_data["text"]
                    logger.info(
                        f"Received transcript for client {client_id}: {text}")

                    # Отправляем транскрипт клиенту
                    await websocket.send_json({
                        "client_id": client_id,
                        "text": text,
                        "status": "transcript"
                    })
                    logger.info(f"Sent transcript to client {client_id}")

                except Exception as e:
                    logger.error(
                        f"Error processing transcript for client {client_id}: {e}")
                    await send_error_response(
                        websocket,
                        f"Failed to process transcript: {str(e)}"
                    )

    except Exception as e:
        logger.error(f"Transcript listener error for client {client_id}: {e}")
    finally:
        await pubsub.unsubscribe(TRANSCRIPTS_CHANNEL)
        await pubsub.close()
        logger.info(
            f"Client {client_id} unsubscribed from transcripts channel")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Обрабатывает аудио-чанки клиента и отсылает транскрипты."""
    await websocket.accept()
    client_id = id(websocket)
    logger.info(f"Client {client_id} connected")

    redis = await get_redis_client()
    transcript_task = None

    try:
        # Создаем задачу для прослушивания транскриптов
        transcript_task = asyncio.create_task(
            listen_transcripts(redis, websocket, client_id)
        )

        # Основной цикл обработки аудио данных
        while True:
            try:
                data = await websocket.receive_bytes()

                # Валидируем аудио данные
                is_valid, error_msg = validate_audio_data(data)
                if not is_valid:
                    logger.error(
                        f"Invalid audio data from client {client_id}: {error_msg}")
                    await send_error_response(
                        websocket, error_msg or "Invalid audio data"
                    )
                    continue

                logger.info(
                    f"Received audio chunk from client {client_id}: "
                    f"{len(data)} bytes"
                )

                # Публикуем бинарные данные в Redis
                audio_b64 = base64.b64encode(data).decode('utf-8')
                await redis.publish(
                    AUDIO_CHANNEL,
                    json.dumps({"client_id": client_id, "audio": audio_b64})
                )
                logger.info(
                    f"Published audio chunk to Redis for client {client_id}")

                # Отправляем подтверждение клиенту
                await websocket.send_json({
                    "status": "received",
                    "size": len(data)
                })

            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(
                    f"Error processing audio for client {client_id}: {e}")
                await send_error_response(
                    websocket,
                    f"Failed to process audio: {str(e)}"
                )

    except Exception as e:
        logger.error(f"Error for client {client_id}: {e}")
        await websocket.close()
    finally:
        # Очистка ресурсов
        if transcript_task:
            transcript_task.cancel()
            try:
                await transcript_task
            except Exception:
                pass
        await redis.close()
        logger.info(f"Client {client_id} cleanup completed")
