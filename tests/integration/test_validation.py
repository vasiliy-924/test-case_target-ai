#!/usr/bin/env python3
import asyncio
import websockets
import json
import time


async def test_validation_and_error_handling():
    """
    Тест валидации и обработки ошибок.
    """
    uri = "ws://localhost:8000/ws"

    try:
        print("🔗 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")

            # Тест 1: Отправка пустых данных
            print("\n📤 Test 1: Sending empty data...")
            await websocket.send(b"")

            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {data}")

            if data.get("status") == "error" and "empty" in data.get("error", ""):
                print("✅ Empty data validation PASSED")
            else:
                print("❌ Empty data validation FAILED")
                return False

            # Тест 2: Отправка слишком больших данных
            print("\n📤 Test 2: Sending large data...")
            large_data = b"x" * (1024 * 1024 + 1)  # Больше 1MB
            await websocket.send(large_data)

            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {data}")

            if data.get("status") == "error" and "large" in data.get("error", ""):
                print("✅ Large data validation PASSED")
            else:
                print("❌ Large data validation FAILED")
                return False

            # Тест 3: Отправка корректных данных
            print("\n📤 Test 3: Sending valid data...")
            valid_data = b"valid audio chunk data"
            await websocket.send(valid_data)

            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {data}")

            if data.get("status") == "received" and data.get("size") == len(valid_data):
                print("✅ Valid data processing PASSED")
            else:
                print("❌ Valid data processing FAILED")
                return False

            # Тест 4: Ждем транскрипт
            print("\n⏳ Waiting for transcript...")
            start_time = time.time()

            while time.time() - start_time < 10:
                try:
                    transcript_response = await asyncio.wait_for(
                        websocket.recv(), timeout=1.0
                    )
                    data = json.loads(transcript_response)
                    print(f"📝 Received: {data}")

                    if data.get("status") == "transcript" and "text" in data:
                        print("✅ Transcript processing PASSED")
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
    success = asyncio.run(test_validation_and_error_handling())
    exit(0 if success else 1)
