# === Встроенные библиотеки
# Библиотека для парсинга аргументов (путь до файла настроек, например)
import argparse

# Прочие библиотеки
import json

# Подключение внутренних модулей
from core.db import prepare_database

# === Внешние библиотеки
# Библиотека для взаимодействия с Telegram API
from aiogram import Dispatcher

# Инициализация т.н. Диспетчера (корневого Роутера) для работы с ботом
dp = Dispatcher()

if __name__ == "main":
    prepare_database()