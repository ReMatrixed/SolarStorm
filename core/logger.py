# Подключение встроенной библиотеки логгирования
import logging

# Настройка логгера
internal_log = logging.getLogger(__name__)
logging.basicConfig(filename = "starstorm.log", level = logging.DEBUG)