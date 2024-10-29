# Подключение библиотеки для работы с файлами локализации (.json)
import json

# Подключение библиотеки логгирования
import logging

# Класс для языкового обработчика
class LanguageDispatcher:
    # Словарь для хранения строк сообщений
    messages: dict
    censorship: list
    # Объект логгера
    logger: logging.Logger

    # Инциализация модуля, чтение данных
    def __init__(self, locale_file_path: str, censorship_file_path: str, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.info("Подготовка языкового диспетчера...")
        self.logger.info(f"Чтение файла локализации ({locale_file_path})...")
        with open(locale_file_path, "r") as locale_file:
            self.messages = json.load(locale_file)
        self.logger.info(f"Чтение файла цензуры (мат-фильтр) ({censorship_file_path})...")
        with open(censorship_file_path, "r") as censorship_file:
            self.censorship = censorship_file.read().replace("\n", " ").split(" ")
        self.logger.info("Языковой диспетчер инициализирован.")

    # Получение значения локализации по ключу
    def get_str(self, key: str) -> str:
        source_str = self.messages.get(key)
        if(source_str != None):
            # Если значение существует, функция возвращает его
            return source_str
        else:
            # Если значение не найдено в файле локализации, возвращается "заглушка"
            return "UNKNOWN"
        
    def is_correct(self, text: str) -> bool:
        text = text.lower() # Приведение всей строки под единый (нижний) регистр
        for bad_word in self.censorship: 
            if(bad_word in text): # Если в тексте содержится нецензурное слово,
                return False      # возвращается False
        return True