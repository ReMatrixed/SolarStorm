# Сборка зависимостей
FROM python:3.12-slim AS image-builder

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .
CMD ["python", "main.py", "-c", "config.json"] 