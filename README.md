<h1 align="center">SolarStorm</h1>
<p align="center"><i>Telegram-бот для чат-центра Светогорской Школы</i></p>

# Начало работы
Для развертывания бота доступно 2 метода: классический и docker-контейнер.
> [!WARNING]
> Для запуска бота потребуется база данных *PostgreSQL*, параметры подключения к которой указываются в *файле конфигурации*.

## Способ 1: *Классический*
*Для запуска чат-бота можно использовать Python 3.12, установив зависимости и указав путь до файла конфигурации:*
``` bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py -c config/config.json
```

## Способ 2: *Docker-контейнер*
> [!WARNING]
> Данный метод - *экспериментальный*. Не рекомендуется использовать его для production-развертывания

> [!TIP]
> Пример развертывания собранного *Docker-image бота* на базе *Docker Compose* с базой данных PostgreSQL доступен в файле *docker/docker-compose.yml*.

Для запуска чат-бота доступно использование *Docker*, предварительно *собрав контейнер из Dockerfile* и *пробросив папку с файлом конфигурации*:
``` bash
sudo docker build -t solarstorm .
sudo docker run -d --restart unless-stopped -v ./config:/config solarstorm:latest
```