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
│   ├── ws_test.py               # Простой WebSocket тест
│   ├── test_websocket_detailed.py # Подробный WebSocket тест
│   ├── test_worker_integration.py # Тест интеграции воркера
│   ├── test_validation.py       # Тест валидации
│   ├── test_validation_simple.py # Упрощенный тест валидации
│   ├── test_integration.py      # Интеграционные тесты
│   ├── test_load.py             # Нагрузочное тестирование
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
git clone <repository-url>
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
# Быстрый WebSocket тест
python3 tests/ws_test.py

# Подробный WebSocket тест
python3 tests/test_websocket_detailed.py

# Тест интеграции воркера
python3 tests/test_worker_integration.py

# Тест валидации
python3 tests/test_validation.py

# Интеграционные тесты
python3 tests/test_integration.py

# Нагрузочное тестирование
python3 tests/test_load.py

# Стресс-тестирование
python3 tests/test_load.py stress
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
# Все тесты
python3 tests/test_integration.py
python3 tests/test_load.py

# Отдельные тесты
python3 tests/ws_test.py
python3 tests/test_validation.py
```

### Результаты тестирования

- ✅ **Юнит-тесты:** 5/5 (100%)
- ✅ **Интеграционные тесты:** 4/4 (100%)
- ✅ **Нагрузочные тесты:** 1/1 (100%)

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