# Подключение библиотеки для работы с файлами локализации (.json)
import json

# Класс для обработчика локализации
class LocalizationDispatcher:
    # Словарь для хранения строк сообщений
    messages: dict

    # Инициализация модуля состоит в чтении файла локализации 
    def __init__(self, filename: str):
        with open(filename, "r") as locale_file:
            self.messages = json.load(locale_file)