# Подключение библиотеки для работы с файлами локализации (.json)
import json

import logging

# Класс для обработчика локализации
class LocalizationDispatcher:
    # Словарь для хранения строк сообщений
    messages: dict
    logger: logging.Logger

    # Инициализация модуля состоит в чтении файла локализации 
    def __init__(self, filename: str, logger: logging.Logger):
        self.logger = logger
        self.logger.info("Подготовка диспетчера локалиизаций...")
        self.logger.info(f"Чтение файла: {filename}...")
        with open(filename, "r") as locale_file:
            self.messages = json.load(locale_file)
        self.logger.info("Диспетчер локализаций инициализирован.")

    # Получение значения по ключу
    def get_str(self, key: str):
        source_str = self.messages.get(key)
        if(source_str != None):
            return source_str
        else:
            return "UNKNOWN"