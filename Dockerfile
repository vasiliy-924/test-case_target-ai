FROM python:3.10-slim

WORKDIR /app

# Установить distutils, pip и gcc для корректной работы pip и aioredis
RUN apt-get update && \
    apt-get install -y python3-distutils python3-pip gcc && \
    rm -rf /var/lib/apt/lists/*

COPY ./app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/. ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]