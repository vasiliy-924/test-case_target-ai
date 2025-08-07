#!/usr/bin/env python3
"""
Нагрузочное тестирование при параллельных соединениях.
"""
import asyncio
import os
import json
import time
import statistics
import pytest
import websockets

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip(
        "Skipping load tests (set RUN_INTEGRATION=1 to run)",
        allow_module_level=True,
    )

pytestmark = pytest.mark.asyncio


async def load_test_client(client_id, num_messages=10):
    """
    Клиент для нагрузочного тестирования.

    Args:
        client_id (int): ID клиента
        num_messages (int): Количество сообщений для отправки

    Returns:
        dict: Результаты тестирования
    """
    uri = "ws://localhost:8000/ws"
    results = {
        "client_id": client_id,
        "connected": False,
        "messages_sent": 0,
        "messages_received": 0,
        "transcripts_received": 0,
        "errors": 0,
        "response_times": [],
        "start_time": time.time(),
        "end_time": None
    }

    try:
        async with websockets.connect(uri) as websocket:
            results["connected"] = True

            # Отправляем сообщения
            for i in range(num_messages):
                try:
                    test_data = f"client {client_id} message {i}".encode()
                    start_time = time.time()

                    await websocket.send(test_data)

                    # Получаем ответ (может быть подтверждение или транскрипт)
                    response = await websocket.recv()
                    response_time = time.time() - start_time
                    results["response_times"].append(response_time)

                    data = json.loads(response)
                    results["messages_sent"] += 1

                    # Проверяем тип ответа
                    if data.get("status") == "received":
                        results["messages_received"] += 1
                    elif data.get("status") == "error":
                        results["errors"] += 1
                    elif data.get("status") == "transcript":
                        # Это транскрипт, не считаем как ошибку
                        pass

                    # Небольшая пауза между сообщениями
                    await asyncio.sleep(0.1)

                except Exception as e:
                    results["errors"] += 1
                    print(f"❌ Client {client_id} error on message {i}: {e}")

            # Ждем транскрипты
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    transcript_response = await asyncio.wait_for(
                        websocket.recv(), timeout=1.0
                    )
                    data = json.loads(transcript_response)

                    if data.get("status") == "transcript":
                        results["transcripts_received"] += 1

                except asyncio.TimeoutError:
                    break
                except Exception:
                    results["errors"] += 1
                    break

    except Exception as e:
        results["errors"] += 1
        print(f"❌ Client {client_id} connection error: {e}")

    results["end_time"] = time.time()
    return results


async def run_load_test(num_clients=10, messages_per_client=5):
    """
    Запуск нагрузочного тестирования.

    Args:
        num_clients (int): Количество параллельных клиентов
        messages_per_client (int): Количество сообщений на клиента
    """
    header = (
        "🚀 Starting load test with "
        f"{num_clients} clients, {messages_per_client} messages each..."
    )
    print(header)

    # Создаем задачи для всех клиентов
    tasks = [
        load_test_client(i, messages_per_client)
        for i in range(num_clients)
    ]

    # Запускаем все клиенты параллельно
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time

    # Анализируем результаты
    successful_clients = 0
    total_messages_sent = 0
    total_messages_received = 0
    total_transcripts_received = 0
    total_errors = 0
    all_response_times = []

    for result in results:
        if isinstance(result, dict):
            if result["connected"]:
                successful_clients += 1

            total_messages_sent += result["messages_sent"]
            total_messages_received += result["messages_received"]
            total_transcripts_received += result["transcripts_received"]
            total_errors += result["errors"]
            all_response_times.extend(result["response_times"])

    # Вычисляем статистику
    avg_response_time = statistics.mean(
        all_response_times) if all_response_times else 0
    min_response_time = min(all_response_times) if all_response_times else 0
    max_response_time = max(all_response_times) if all_response_times else 0

    # Выводим результаты
    print(f"\n{'='*60}")
    print("LOAD TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Successful clients: {successful_clients}/{num_clients}")
    print(f"Messages sent: {total_messages_sent}")
    print(f"Messages received: {total_messages_received}")
    print(f"Transcripts received: {total_transcripts_received}")
    print(f"Total errors: {total_errors}")
    print(f"Average response time: {avg_response_time:.3f}s")
    print(f"Min response time: {min_response_time:.3f}s")
    print(f"Max response time: {max_response_time:.3f}s")
    print(f"Messages per second: {total_messages_sent/total_time:.2f}")

    # Оценка производительности
    success_rate = successful_clients / num_clients
    message_success_rate = total_messages_received / \
        total_messages_sent if total_messages_sent > 0 else 0
    transcript_rate = total_transcripts_received / \
        total_messages_sent if total_messages_sent > 0 else 0

    print("\nPERFORMANCE METRICS")
    print(f"{'='*60}")
    print(f"Client success rate: {success_rate:.1%}")
    print(f"Message success rate: {message_success_rate:.1%}")
    print(f"Transcript rate: {transcript_rate:.1%}")

    # Определяем статус теста
    if success_rate >= 0.8 and total_errors < num_clients:
        print("\n✅ Load test PASSED")
        return True
    else:
        print("\n❌ Load test FAILED")
        return False


async def run_stress_test():
    """
    Стресс-тест с большим количеством клиентов.
    """
    print("🔥 Running stress test...")

    # Тест 1: Много клиентов, мало сообщений
    print("\nTest 1: Many clients, few messages")
    result1 = await run_load_test(num_clients=20, messages_per_client=3)

    # Тест 2: Меньше клиентов, больше сообщений
    print("\nTest 2: Few clients, many messages")
    result2 = await run_load_test(num_clients=5, messages_per_client=20)

    # Тест 3: Сбалансированный тест
    print("\nTest 3: Balanced test")
    result3 = await run_load_test(num_clients=15, messages_per_client=10)

    overall_success = result1 and result2 and result3
    summary = (
        "\n📊 Overall stress test: "
        f"{'✅ PASSED' if overall_success else '❌ FAILED'}"
    )
    print(summary)

    return overall_success


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stress":
        success = asyncio.run(run_stress_test())
    else:
        success = asyncio.run(run_load_test())

    exit(0 if success else 1)


# Pytest entrypoint for CI/integration runs
@pytest.mark.asyncio
async def test_load_quick():
    """Quick load test under pytest to validate performance path."""
    result = await run_load_test(num_clients=5, messages_per_client=3)
    assert result is True


@pytest.mark.asyncio
async def test_load_stress():
    """Stress load test under pytest to validate stability under pressure."""
    result = await run_stress_test()
    assert result is True
