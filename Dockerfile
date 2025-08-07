FROM python:3.10-slim

WORKDIR /app

# Base OS deps (gcc часто нужен для wheels, можно удалить при оптимизации)
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Копируем зависимости из корневого requirements.txt
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники приложения
COPY ./app/. ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]