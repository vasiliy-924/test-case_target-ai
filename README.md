# WebSocket Audio Processing Service

Сервис для обработки аудио данных через WebSocket соединения с использованием FastAPI, Redis и асинхронной архитектуры.

## 🏗️ Архитектура

Система построена на микросервисной архитектуре с использованием:

- **FastAPI** - высокопроизводительный веб-фреймворк для API
- **Redis** - in-memory база данных для pub/sub сообщений
- **WebSocket** - протокол для двусторонней связи в реальном времени
- **Docker** - контейнеризация для упрощения развертывания

### Архитектурная схема

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Web Client    │ ──────────────► │   FastAPI App   │
│                 │                 │                 │
│ - Browser       │                 │ - WebSocket     │
│ - Mobile App    │                 │ - Validation    │
│ - Desktop App   │                 │ - Error Handling│
└─────────────────┘                 └─────────────────┘
                                              │
                                              │ Redis Pub/Sub
                                              ▼
┌─────────────────┐                 ┌─────────────────┐
│   Worker        │ ◄────────────── │     Redis       │
│                 │                 │                 │
│ - Audio         │                 │ - audio_chunks  │
│   Processing    │                 │ - transcripts   │
│ - Transcription │                 │ - Pub/Sub       │
└─────────────────┘                 └─────────────────┘
```

## 📁 Структура проекта

```
test-case_target-ai/
├── app/                           # Основное приложение
│   ├── main.py                   # FastAPI приложение
│   ├── ws.py                     # WebSocket обработчики
│   ├── workers.py                # Фоновые задачи
│   ├── redis_client.py           # Redis утилиты
│   ├── config.py                 # Конфигурация
│   └── requirements.txt          # Зависимости Python
├── static/                       # Статические файлы
│   ├── test_websocket.html      # HTML страница для тестирования
│   └── README.md                # Описание статических файлов
├── tests/                        # Тесты
│   ├── integration/             # Интеграционные и валидационные тесты
│   │   ├── test_integration.py
│   │   ├── test_worker_integration.py
│   │   ├── test_validation.py
│   │   └── test_validation_simple.py
│   ├── websocket/               # Тесты WebSocket соединения
│   │   ├── ws_test.py
│   │   └── test_websocket_detailed.py
│   ├── load/                    # Нагрузочные тесты
│   │   └── test_load.py
│   ├── test_redis_unit.py       # Юнит-тесты для Redis и WebSocket-логики
│   └── README.md                # Описание тестов
├── docker-compose.yml            # Docker Compose конфигурация
├── Dockerfile                    # Docker образ
├── .env                          # Переменные окружения
└── README.md                     # Этот файл
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.10+ (для локального тестирования)
- Git

### 1. Клонирование и запуск

```bash
# Клонируйте репозиторий
git clone git@github.com:vasiliy-924/test-case_target-ai.git
cd test-case_target-ai

# Запустите все сервисы
docker-compose up -d

# Или запустите с воркером отдельно
docker-compose up -d
docker-compose up worker -d
```

### 2. Проверка работоспособности

```bash
# Проверьте статус сервисов
docker-compose ps

# Проверьте HTTP API
curl http://localhost:8000/
# Ответ: {"message":"WebSocket Service is running"}

# Проверьте конфигурацию
curl http://localhost:8000/config
# Ответ: {"APP_PORT":8000,"REDIS_URL":"redis://redis:6379/0"}

# Проверьте Redis
docker exec redis redis-cli ping
# Ответ: PONG
```

### 3. Тестирование

```bash
# Активация .venv
source .venv/bin/activate

# Все юнит-тесты (без Docker)
pytest -q

# Все тесты, включая интеграционные и нагрузочные (нужен Docker)
docker compose up -d --build
RUN_INTEGRATION=1 pytest -q

# Только нагрузочные
RUN_INTEGRATION=1 pytest tests/load/test_load.py -q
```

### 4. Веб-интерфейс

Откройте в браузере:
```
file:///path/to/project/static/test_websocket.html
```

## 🔌 WebSocket API

### Подключение

**URL:** `ws://localhost:8000/ws`

### Отправка аудио данных

```javascript
// Подключение
const ws = new WebSocket('ws://localhost:8000/ws');

// Отправка бинарных данных
ws.send(audioData); // ArrayBuffer или Blob
```

### Получение ответов

#### Подтверждение получения
```json
{
  "status": "received",
  "size": 1024
}
```

#### Транскрипт
```json
{
  "client_id": 123456789,
  "text": "Transcribed: 2025-08-06 20:04:42 (size: 1024 bytes)",
  "status": "transcript"
}
```

#### Ошибка валидации
```json
{
  "error": "Audio data is empty",
  "status": "error"
}
```

### Примеры использования

#### JavaScript (браузер)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
  
  // Отправка аудио данных
  const audioData = new ArrayBuffer(1024);
  ws.send(audioData);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.status === 'received') {
    console.log(`Audio received: ${data.size} bytes`);
  } else if (data.status === 'transcript') {
    console.log(`Transcript: ${data.text}`);
  } else if (data.status === 'error') {
    console.error(`Error: ${data.error}`);
  }
};
```

#### Python
```python
import asyncio
import websockets
import json

async def send_audio():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Отправка аудио данных
        audio_data = b"test audio data"
        await websocket.send(audio_data)
        
        # Получение подтверждения
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received: {data}")
        
        # Получение транскрипта
        transcript = await websocket.recv()
        data = json.loads(transcript)
        print(f"Transcript: {data}")

asyncio.run(send_audio())
```

## ⚙️ Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Порт приложения
APP_PORT=8000

# URL подключения к Redis
REDIS_URL=redis://redis:6379/0

# Дополнительные настройки (опционально)
LOG_LEVEL=INFO
MAX_AUDIO_SIZE=1048576  # 1MB в байтах
```

### Docker Compose сервисы

#### FastAPI App (`app`)
- **Порт:** 8000
- **Команда:** `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
- **Зависимости:** Redis

#### Redis (`redis`)
- **Порт:** 6379
- **Образ:** redis:7-alpine
- **Том:** redis_data

#### Worker (`worker`)
- **Команда:** `python workers.py`
- **Зависимости:** Redis
- **Функция:** Обработка аудио и создание транскриптов

### Валидация данных

#### Аудио данные
- **Максимальный размер:** 1MB
- **Формат:** Бинарные данные
- **Валидация:** Непустые данные

#### Транскрипты
- **Формат:** UTF-8 текст
- **Валидация:** Непустой текст

## 🧪 Тестирование

### Типы тестов

1. **Юнит-тесты** - тестирование отдельных компонентов
2. **Интеграционные тесты** - тестирование взаимодействия компонентов
3. **Нагрузочные тесты** - тестирование производительности

### Запуск тестов

```bash
# Все юнит-тесты
pytest -q

# Интеграция и нагрузка (ввести для тестирования)
RUN_INTEGRATION=1 pytest -q
```

### Результаты тестирования (локально)

- ✅ Все тесты прошли: `23 passed` (включая нагрузочные)

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Логи приложения
docker logs fastapi-app

# Логи воркера
docker logs transcription-worker

# Логи Redis
docker logs redis
```

### Метрики производительности

- **Время отклика:** ~2ms
- **Пропускная способность:** ~32 сообщения/сек
- **Успешность клиентов:** 100%
- **Максимальные соединения:** 20+ параллельных клиентов

## 🔧 Разработка

### Локальная разработка

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r app/requirements.txt

# Запуск в режиме разработки
cd app
uvicorn main:app --reload
```

### Добавление новых функций

1. **WebSocket обработчики:** `app/ws.py`
2. **Фоновые задачи:** `app/workers.py`
3. **Redis утилиты:** `app/redis_client.py`
4. **Конфигурация:** `app/config.py`

### Структура кода

- **Асинхронное программирование:** Все I/O операции асинхронные
- **Обработка ошибок:** Валидация и graceful degradation
- **Логирование:** Структурированные логи
- **Тестирование:** Покрытие всех критических путей

## 🚀 Развертывание

### Продакшен

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml up -d

# Проверка здоровья
curl http://localhost:8000/health
```

### Масштабирование

```bash
# Масштабирование воркеров
docker-compose up --scale worker=3 -d

# Масштабирование приложений
docker-compose up --scale app=2 -d
```

## 📝 Выполнил тестовое задание
**Василий Петров** - [GitHub https://github.com/vasiliy-924](https://github.com/vasiliy-924)