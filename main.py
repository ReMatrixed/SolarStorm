# Подключение встроенных библиотек
import argparse
import logging
import json
import asyncio
import os

# Подключение внутренних модулей
from core.db import DatabaseDispatcher, UserData
from core.locale import LocalizationDispatcher

# Библиотеки для взаимодействия с Telegram API
from aiogram import Dispatcher, Bot, types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Инициализация парсера аргументов командной строки
arg_parser = argparse.ArgumentParser(
    prog = "SolarStorm Telegram-Bot",
    description = "Телеграм-бот для чат-центра Светогоской Школы"
)
arg_parser.add_argument("-c", "--config", required = True)
args = arg_parser.parse_args()

logging.basicConfig(
    filename = "solarstorm.log", 
    encoding = "utf-8",
    level = logging.DEBUG,
)
logger = logging.getLogger("main.py")
logger.info("===========================")
logger.info("Запуск SOLARSTORM V0.1.0...")

with open(args.config, "r") as config_file:
    cfg = json.load(config_file)

# Инициализация внутренних модулей
db = DatabaseDispatcher()
ll = LocalizationDispatcher("resources/messages_ru.json", logger)

dp = Dispatcher()
bot = Bot(cfg.get("bot.api_key"))

class NewbieDialog(StatesGroup):
    question_name = State()
    question_form = State()
    question_school = State()

@dp.callback_query(F.text == "statistics_disallow")
async def disallow_statistics_callback(callback: types.CallbackQuery):
    userdata = UserData(
        callback.from_user.id, "user", 0, "Аноним", 0, "СКРЫТ"
    )
    await db.add_entry(userdata)
    await callback.message.answer(ll.get_str("greeting.newbie.finish"))
    await callback.answer()

@dp.callback_query(F.text == "statistics_allow")
async def allow_statistics_callback(callback: types.CallbackQuery):
    await callback.answer()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    available_users = await db.get_entry(message.from_user.id)
    if(available_users == None):
        buttons = [
            types.InlineKeyboardButton(text="Да ✅", callback_data="statistics_allow"),
            types.InlineKeyboardButton(text="Нет ❌", callback_data="statistics_disallow")
        ],
        await message.answer(ll.get_str("greeting.newbie"), reply_markup = types.InlineKeyboardMarkup(inline_keyboard = buttons))
    else:
        await message.answer(ll.get_str("greeting.known").replace("&&1", available_users[4]))
    
async def run_system():
    await db.setup(
        cfg.get("db.host"),
        cfg.get("db.port"),
        cfg.get("db.username"),
        cfg.get("db.password"),
        cfg.get("db.name"),
        logger
    )
    await db.prepare_database()
    await dp.start_polling(bot)

# Основной код 
if __name__ == "__main__":
    asyncio.run(run_system())