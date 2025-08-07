#!/usr/bin/env python3
"""
Интеграционные тесты для проверки полного цикла работы системы.
"""
import asyncio
import websockets
import json
import time


async def test_single_client_integration():
    """
    Тест интеграции с одним клиентом.
    """
    print("🔗 Testing single client integration...")

    uri = "ws://localhost:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")

            # Отправляем несколько аудио чанков
            for i in range(3):
                test_data = f"audio chunk {i}".encode()
                print(f"📤 Sending chunk {i}: {len(test_data)} bytes")
                await websocket.send(test_data)

                # Получаем подтверждение
                response = await websocket.recv()
                data = json.loads(response)
                print(f"📥 Confirmation: {data}")

                assert data["status"] == "received"
                assert data["size"] == len(test_data)

            # Ждем транскрипты
            print("⏳ Waiting for transcripts...")
            transcripts_received = 0

            start_time = time.time()
            while time.time() - start_time < 15 and transcripts_received < 3:
                try:
                    transcript_response = await asyncio.wait_for(
                        websocket.recv(), timeout=2.0
                    )
                    data = json.loads(transcript_response)
                    print(f"📝 Transcript {transcripts_received + 1}: {data}")

                    if data.get("status") == "transcript" and "text" in data:
                        transcripts_received += 1

                except asyncio.TimeoutError:
                    print("⏰ Still waiting...")
                    continue

            print(f"✅ Received {transcripts_received} transcripts")
            return transcripts_received >= 2  # Хотя бы 2 транскрипта

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_multiple_clients():
    """
    Тест с несколькими клиентами одновременно.
    """
    print("🔗 Testing multiple clients...")

    uri = "ws://localhost:8000/ws"
    num_clients = 3
    results = []

    async def client_task(client_id):
        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ Client {client_id} connected")

                # Отправляем данные
                test_data = f"client {client_id} audio".encode()
                await websocket.send(test_data)

                # Получаем подтверждение
                response = await websocket.recv()
                data = json.loads(response)

                # Ждем транскрипт
                start_time = time.time()
                while time.time() - start_time < 10:
                    try:
                        transcript_response = await asyncio.wait_for(
                            websocket.recv(), timeout=2.0
                        )
                        data = json.loads(transcript_response)

                        if data.get("status") == "transcript":
                            print(f"✅ Client {client_id} received transcript")
                            return True

                    except asyncio.TimeoutError:
                        continue

                print(f"❌ Client {client_id} timeout")
                return False

        except Exception as e:
            print(f"❌ Client {client_id} error: {e}")
            return False

    # Запускаем клиентов параллельно
    tasks = [client_task(i) for i in range(num_clients)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_clients = sum(1 for r in results if r is True)
    print(f"📊 Results: {successful_clients}/{num_clients} clients successful")

    return successful_clients >= 2  # Хотя бы 2 клиента должны работать


async def test_error_handling():
    """
    Тест обработки ошибок.
    """
    print("🔗 Testing error handling...")

    uri = "ws://localhost:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")

            # Тест 1: Отправка пустых данных
            print("📤 Sending empty data...")
            await websocket.send(b"")

            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {data}")

            if data.get("status") == "error":
                print("✅ Empty data error handling PASSED")
            else:
                print("❌ Empty data error handling FAILED")
                return False

            # Тест 2: Отправка корректных данных
            print("📤 Sending valid data...")
            valid_data = b"valid audio data"
            await websocket.send(valid_data)

            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {data}")

            if data.get("status") == "received":
                print("✅ Valid data handling PASSED")
                return True
            else:
                print("❌ Valid data handling FAILED")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_worker_integration():
    """
    Тест интеграции с воркером.
    """
    print("🔗 Testing worker integration...")

    # Проверяем, что воркер запущен
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=transcription-worker"],
            capture_output=True, text=True
        )
        if "transcription-worker" not in result.stdout:
            print("❌ Worker not running")
            return False
        print("✅ Worker is running")
    except Exception as e:
        print(f"❌ Cannot check worker status: {e}")
        return False

    # Тестируем полный цикл
    uri = "ws://localhost:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")

            # Отправляем данные
            test_data = b"test audio for worker integration"
            print(f"📤 Sending data: {len(test_data)} bytes")
            await websocket.send(test_data)

            # Получаем подтверждение
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Confirmation: {data}")

            # Ждем транскрипт от воркера
            print("⏳ Waiting for worker transcript...")
            start_time = time.time()

            while time.time() - start_time < 10:
                try:
                    transcript_response = await asyncio.wait_for(
                        websocket.recv(), timeout=2.0
                    )
                    data = json.loads(transcript_response)
                    print(f"📝 Worker transcript: {data}")

                    if data.get("status") == "transcript" and "text" in data:
                        if "Transcribed:" in data["text"]:
                            print("✅ Worker integration PASSED")
                            return True

                except asyncio.TimeoutError:
                    print("⏰ Still waiting for worker...")
                    continue

            print("❌ No worker transcript received")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def run_all_integration_tests():
    """
    Запуск всех интеграционных тестов.
    """
    print("🚀 Starting integration tests...\n")

    tests = [
        ("Single Client Integration", test_single_client_integration),
        ("Multiple Clients", test_multiple_clients),
        ("Error Handling", test_error_handling),
        ("Worker Integration", test_worker_integration)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")

        try:
            result = await test_func()
            results.append((test_name, result))

            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")

        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))

    # Итоговый отчет
    print(f"\n{'='*50}")
    print("INTEGRATION TEST RESULTS")
    print(f"{'='*50}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\n📊 Overall: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_integration_tests())
    exit(0 if success else 1)
