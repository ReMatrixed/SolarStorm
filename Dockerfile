FROM python:3.12-slim
WORKDIR /app

COPY core /app
COPY resources /app
COPY config /app
COPY main.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt
CMD ["python", "./main.py", "-c", "/config/config.json"] 