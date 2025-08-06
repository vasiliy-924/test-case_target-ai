#!/usr/bin/env python3
import asyncio
import websockets
import json
import time


async def test_worker_integration():
    """
    Тест полной интеграции: WebSocket -> Redis -> Worker -> Transcript
    """
    uri = "ws://localhost:8000/ws"
    
    try:
        print("🔗 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")
            
            # Отправляем аудио данные
            test_audio = b"test audio chunk for worker processing"
            print(f"📤 Sending audio chunk: {len(test_audio)} bytes")
            await websocket.send(test_audio)
            
            # Получаем подтверждение
            response = await websocket.recv()
            print(f"📥 Received confirmation: {response}")
            
            # Ждем транскрипт (максимум 10 секунд)
            print("⏳ Waiting for transcript...")
            start_time = time.time()
            
            while time.time() - start_time < 10:
                try:
                    transcript_response = await asyncio.wait_for(
                        websocket.recv(), timeout=1.0
                    )
                    data = json.loads(transcript_response)
                    print(f"📝 Received transcript: {data}")
                    
                    if "text" in data:
                        print("✅ Worker integration test PASSED!")
                        return True
                        
                except asyncio.TimeoutError:
                    print("⏰ Still waiting for transcript...")
                    continue
                    
            print("❌ No transcript received within 10 seconds")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_worker_integration())
    exit(0 if success else 1) 