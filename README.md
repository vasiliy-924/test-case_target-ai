# WebSocket Audio Processing Service

Сервис для обработки аудио данных через WebSocket соединения с использованием FastAPI и Redis.

## Структура проекта

```
test-case_target-ai/
├── app/                    # Основное приложение
│   ├── main.py            # FastAPI приложение
│   ├── ws.py              # WebSocket обработчики
│   ├── config.py          # Конфигурация
│   ├── workers.py         # Фоновые задачи
│   └── requirements.txt   # Зависимости Python
├── static/                # Статические файлы
│   ├── test_websocket.html # HTML страница для тестирования
│   └── README.md          # Описание статических файлов
├── tests/                 # Тесты
│   ├── ws_test.py        # Простой WebSocket тест
│   ├── test_websocket_detailed.py # Подробный WebSocket тест
│   └── README.md         # Описание тестов
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile             # Docker образ
└── README.md              # Этот файл
```

## Быстрый старт

1. Запустите сервисы:
   ```bash
   docker-compose up -d
   ```

2. Проверьте работу сервиса:
   ```bash
   curl http://localhost:8000/
   ```

3. Протестируйте WebSocket:
   ```bash
   # Быстрый тест
   python3 tests/ws_test.py
   
   # Подробный тест
   python3 tests/test_websocket_detailed.py
   ```

4. Откройте в браузере:
   ```
   file:///path/to/project/static/test_websocket.html
   ```

## WebSocket API

- **URL**: `ws://localhost:8000/ws`
- **Протокол**: Отправка бинарных аудио данных
- **Ответы**: JSON с статусом и размером данных

## Разработка

- Приложение автоматически перезагружается при изменениях
- Логи доступны через `docker logs fastapi-app`
- Redis доступен на порту 6379 