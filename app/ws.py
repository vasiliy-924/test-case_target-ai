from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import aioredis
import asyncio

from config import get_redis_url

router = APIRouter()

REDIS_CHANNEL = "audio_chunks"
TRANSCRIPTS_CHANNEL = "transcripts"

async def get_redis():
    return await aioredis.from_url(get_redis_url(), decode_responses=False)

async def listen_transcripts(redis, websocket, client_id):
    pubsub = redis.pubsub()
    await pubsub.subscribe(TRANSCRIPTS_CHANNEL)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Предполагаем, что message["data"] — это текст транскрипта (bytes)
                text = message["data"].decode("utf-8", errors="ignore")
                await websocket.send_json({"client_id": client_id, "text": text})
    except Exception as e:
        print(f"Transcript listener error for client {client_id}: {e}")
    finally:
        await pubsub.unsubscribe(TRANSCRIPTS_CHANNEL)
        await pubsub.close()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)
    print(f"Client {client_id} connected")
    redis = await get_redis()
    transcript_task = None
    try:
        transcript_task = asyncio.create_task(listen_transcripts(redis, websocket, client_id))
        while True:
            data = await websocket.receive_bytes()
            print(f"Received audio chunk from client {client_id}: {len(data)} bytes")
            # Публикуем бинарные данные в Redis
            await redis.publish(REDIS_CHANNEL, data)
            await websocket.send_json({"status": "received", "size": len(data)})
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"Error for client {client_id}: {e}")
        await websocket.close()
    finally:
        if transcript_task:
            transcript_task.cancel()
            try:
                await transcript_task
            except Exception:
                pass
        await redis.close()