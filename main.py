# === Встроенные библиотеки
# Библиотека для парсинга аргументов (API-ключ, например)
import argparse
# Прочие библиотеки
import logging

# === Внешние библиотеки
# Библиотека для взаимодействия с Telegram API
import aiogram

# Настройка логгера
log = logging.getLogger(__name__)
logging.basicConfig(filename = "starstorm.log", level = logging.DEBUG)