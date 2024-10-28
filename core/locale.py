# Подключение библиотеки для работы с файлами локализации (.json)
import json

# Подключение библиотеки логгирования
import logging

# Класс для языкового обработчика
class LanguageDispatcher:
    # Словарь для хранения строк сообщений
    messages: dict
    # Объект логгера
    logger: logging.Logger

    # Инциализация модуля, чтение данных локализации
    def __init__(self, filename: str, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.info("Подготовка диспетчера локалиизаций...")
        self.logger.info(f"Чтение файла: {filename}...")
        with open(filename, "r") as locale_file:
            self.messages = json.load(locale_file)
        self.logger.info("Диспетчер локализаций инициализирован.")

    # Получение значения локализации по ключу
    def get_str(self, key: str) -> str:
        source_str = self.messages.get(key)
        if(source_str != None):
            # Если значение существует, функция возвращает его
            return source_str
        else:
            # Если значение не найдено в файле локализации, возвращается "заглушка"
            return "UNKNOWN"