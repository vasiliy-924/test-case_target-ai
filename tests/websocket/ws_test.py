import asyncio
import websockets


async def test_ws():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Отправим бинарные данные (например, 10 байт)
        await websocket.send(b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A')
        # Получим ответ
        response = await websocket.recv()
        print("Ответ сервера:", response)

asyncio.run(test_ws())
