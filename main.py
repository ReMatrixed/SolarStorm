# Подключение встроенных библиотек
import argparse
import logging
import json

# Подключение внутренних модулей
from core.db import DatabaseDispatcher

# Инициализация парсера аргументов командной строки
arg_parser = argparse.ArgumentParser(
    prog = "StarStorm Telegram-Bot",
    description = "Телеграм-бот для чат-центра Светогоской Школы"
)
arg_parser.add_argument("-c", "--config", required = True)
args = arg_parser.parse_args()

with open(args.config, "r") as config_file:
    cfg = json.load(config_file)

logging.basicConfig(filename = "starstorm.log", encoding = "utf-8")
logger = logging.getLogger(__name__)

db = DatabaseDispatcher(
    cfg.get("db.host"),
    cfg.get("db.port"),
    cfg.get("db.username"),
    cfg.get("db.password"),
    cfg.get("db.name"),
    logger
)

if __name__ == "__main__":
    logger.info("Запуск бота, подождите...")
    db.prepare_database()
    entries = db.get_entries(-1)
    print(entries)
    db.close_database()