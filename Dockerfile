# Сборка зависимостей
FROM python:3.12-slim AS image-builder

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY core core
COPY resources resources
COPY main.py .
COPY config config
CMD ["python", "main.py", "-c", "config/config.json"] 