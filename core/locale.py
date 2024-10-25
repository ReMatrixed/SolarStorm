# Подключение библиотеки для работы с файлами локализации (.json)
import json

# Подключение внутренних модулей
from core.logger import internal_log

# Массив для хранения строк сообщений
messages = []

# Подготовка строк сообщений
def prepare_messages(filename: str):
    internal_log.info("Чтение файла локализации...")
    with open(filename, "r") as locale_file:
        messages = json.load(locale_file)