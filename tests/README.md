# Tests

Эта директория содержит автоматизированные тесты для проверки функциональности приложения.

## Структура

- **integration/** — интеграционные и валидационные тесты
    - test_integration.py
    - test_worker_integration.py
    - test_validation.py
    - test_validation_simple.py
- **websocket/** — тесты WebSocket соединения
    - ws_test.py
    - test_websocket_detailed.py
- **load/** — нагрузочные тесты
    - test_load.py
- **test_redis_unit.py** — юнит-тесты для Redis и WebSocket-логики

## Описание тестов

- **websocket/ws_test.py** — Простой тест WebSocket соединения
  - Проверяет подключение к WebSocket серверу
  - Отправляет тестовые бинарные данные (10 байт)
  - Проверяет получение ответа
  - Минимальный тест для быстрой проверки

- **websocket/test_websocket_detailed.py** — Подробный тест WebSocket соединения
  - Проверяет подключение к WebSocket серверу
  - Отправляет тестовые аудио данные
  - Проверяет получение ответов с таймаутами
  - Ждет дополнительные сообщения
  - Подробное логирование и обработка ошибок

- **integration/test_worker_integration.py** — Тест интеграции воркера
  - Проверяет полный цикл: WebSocket -> Redis -> Worker -> Transcript
  - Отправляет аудио данные через WebSocket
  - Ждет транскрипт от воркера
  - Проверяет корректность полученных данных

- **integration/test_validation.py** — Тест валидации и обработки ошибок
  - Проверяет валидацию пустых данных
  - Проверяет валидацию слишком больших данных (>1MB)
  - Проверяет обработку корректных данных
  - Проверяет получение транскриптов с правильным статусом

- **integration/test_validation_simple.py** — Упрощенный тест валидации
  - Работает локально без внешних зависимостей
  - Тестирует логику валидации данных

- **integration/test_integration.py** — Интеграционные тесты
  - Тест с одним клиентом
  - Тест с несколькими клиентами одновременно
  - Тест обработки ошибок
  - Тест интеграции с воркером

- **load/test_load.py** — Нагрузочное тестирование
  - Тестирует устойчивость при параллельных соединениях
  - Измеряет производительность системы
  - Проверяет обработку множественных клиентов

- **test_redis_unit.py** — Юнит-тесты для логики работы с Redis и WebSocket-обработчиков

## Запуск тестов

```bash
# Установка зависимостей
pip install websockets

# Быстрый тест WebSocket
python3 tests/websocket/ws_test.py

# Подробный тест WebSocket
python3 tests/websocket/test_websocket_detailed.py

# Тест интеграции воркера
python3 tests/integration/test_worker_integration.py

# Тест валидации и обработки ошибок
python3 tests/integration/test_validation.py

# Упрощенный тест валидации
python3 tests/integration/test_validation_simple.py

# Интеграционные тесты
python3 tests/integration/test_integration.py

# Нагрузочное тестирование
python3 tests/load/test_load.py

# Юнит-тесты Redis/WebSocket
python3 tests/test_redis_unit.py
```

## Требования

- Python 3.10+
- websockets библиотека
- Запущенный WebSocket сервер (docker-compose up) 