<h1 align="center">SolarStorm</h1><p align="center"><i>Telegram-бот для чат-центра Светогорской Школы</i></p>

# Начало работы
Для развертывания бота доступно 2 метода: классический и docker-контейнер.

> [!WARNING]
> Для запуска бота потребуется базы данных *PostgreSQL* и *Redis*, параметры подключения к которым указываются в *файле конфигурации*.

## Способ 1: *Классический*
*Для запуска чат-бота можно использовать Python 3.12, установив зависимости и указав путь до файла конфигурации:*
``` bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py -c config/config.json
```

## Способ 2: *Docker-контейнер*
> [!TIP]
> Пример развертывания на базе *Docker Compose* с необходимыми базами данных доступен в файле *docker/docker-compose.yml*.

Для запуска чат-бота также можно использовать развертывание с использованием *Docker Compose*, предварительно настроив параметры подключения к БД в *файле config.json*:
``` yaml
services:
  solarstorm:
    build: .
    container_name: solarstorm
    restart: always
    volumes:
      - ./config.json:/app/config.json
      - ./logs:/app/logs
```
