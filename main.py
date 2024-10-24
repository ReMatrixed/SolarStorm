# Библиотека для парсинга аргументов (API-ключ, например)
import argparse

# Библиотека для взаимодействия с Telegram API
import aiogram

# Прочие библиотеки
import logging

# Настройка логгера
log = logging.getLogger(__name__)
logging.basicConfig(filename = "starstorm.log", level = logging.DEBUG)