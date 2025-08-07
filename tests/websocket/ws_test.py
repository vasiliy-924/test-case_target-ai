import asyncio
import os
import json
import pytest
import websockets

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip(
        "Skipping websocket tests (set RUN_INTEGRATION=1 to run)",
        allow_module_level=True,
    )

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_websocket_simple_connect_and_receive():
    uri = "ws://localhost:8000/ws"

    # Небольшой ретрай, чтобы дождаться готовности сервиса внутри Docker
    last_error = None
    for _ in range(10):
        try:
            async with websockets.connect(uri) as websocket:
                payload = b"test-payload"
                await websocket.send(payload)
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(response)
                assert data.get("status") == "received"
                assert data.get("size") == len(payload)
                return
        except Exception as e:  # noqa: BLE001 - ретрай по любым ошибкам соединения
            last_error = e
            await asyncio.sleep(1)

    raise AssertionError(f"WebSocket not ready, last error: {last_error}")
