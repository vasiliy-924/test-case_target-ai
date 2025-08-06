#!/usr/bin/env python3
import asyncio
import websockets
import sys


async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Отправляем тестовые данные
            test_data = b"test audio chunk data"
            print(f"Sending test data: {len(test_data)} bytes")
            await websocket.send(test_data)
            
            # Ждем ответа
            try:
                response = await asyncio.wait_for(
                    websocket.recv(), timeout=5.0
                )
                print(f"✅ Received response: {response}")
            except asyncio.TimeoutError:
                print("⚠️  No response received within 5 seconds")
            
            # Ждем еще немного для получения возможных сообщений
            print("Waiting for additional messages...")
            try:
                while True:
                    message = await asyncio.wait_for(
                        websocket.recv(), timeout=2.0
                    )
                    print(f"📨 Received: {message}")
            except asyncio.TimeoutError:
                print("No more messages")
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    sys.exit(0 if success else 1) 