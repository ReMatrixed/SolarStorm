# Подключение встроенных библиотек
import argparse
import logging
import json
import asyncio
import os
import re

# Подключение внутренних модулей
from core.db import DatabaseDispatcher, UserData
from core.locale import LocalizationDispatcher

# Подключение модулей библиотеки aiogram для взаимодействия с Telegram Bot API
from aiogram import Dispatcher, Bot, types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

# Инициализация парсера аргументов командной строки
arg_parser = argparse.ArgumentParser(
    prog = "SolarStorm Telegram-Bot",
    description = "Телеграм-бот для чат-центра Светогоской Школы"
)
arg_parser.add_argument("-c", "--config", required = True)
args = arg_parser.parse_args()

# Настройка логгирования в файл
logging.basicConfig(
    filename = "solarstorm.log", 
    encoding = "utf-8",
    level = logging.DEBUG,
)
logger = logging.getLogger("main.py")
logger.info("===========================")
logger.info("Запуск бота SOLARSTORM...")

# Чтение файла конфигурации
with open(args.config, "r") as config_file:
    cfg = json.load(config_file)

# Инициализация внутренних модулей
db = DatabaseDispatcher()
ll = LocalizationDispatcher("resources/messages_ru.json", logger)

# Настройка Telegram-бота
fsm_memory_storage = MemoryStorage()
dp = Dispatcher(storage = fsm_memory_storage)
bot = Bot(cfg.get("bot.api_key"), default = DefaultBotProperties(parse_mode = ParseMode.HTML))

# Состояния FSM, предназначенные для вступительного опроса пользователя
class UserDialog(StatesGroup):
    say_hello = State()
    fill_anonymous = State()
    fill_name = State()
    fill_form = State()
    fill_city = State()
    greet_known_user = State()
    ask_question = State()
    select_subject = State()
    start_dialog = State()
    continue_dialog = State()
    finish_dialog = State()

# Паттерн для проверки корректности имени и фамилии
cyrillic_pattern = re.compile(r"[^а-яёА-ЯЁ\s-]|[\s{2,}] ")

# Callback для ответа на сообщение, касающегося вступительного опроса
@dp.callback_query(StateFilter(UserDialog.fill_anonymous), F.data.startswith("statistics_"))
async def disallow_statistics_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if(callback.data == "statistics_disallow"):
        userdata = UserData(
            available = True,
            chat_id = callback.from_user.id, 
            role = "user", 
            rating = 0, 
            realname = "Аноним", 
            form = 0, 
            city = "СКРЫТ"
        )
        await db.add_entry(userdata)
        await callback.message.reply(ll.get_str("greeting.newbie.finish"))
        await state.set_state(UserDialog.ask_question)
    elif(callback.data == "statistics_allow"):
        await callback.message.reply(ll.get_str("greeting.newbie.realname"))
        await callback.message.answer(ll.get_str("greeting.newbie.realname.warning"))
        await state.set_state(UserDialog.fill_name)

# Handler для команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(UserDialog.say_hello)
    user_data = await db.get_entry(message.from_user.id)
    if(user_data.available):
        await message.answer(ll.get_str("greeting.known").replace("&&1", user_data.realname))
        await state.set_state(UserDialog.ask_question)
    else:
        buttons = [
            types.InlineKeyboardButton(text="Да ✅", callback_data="statistics_allow"),
            types.InlineKeyboardButton(text="Нет ❌", callback_data="statistics_disallow")
        ],
        await message.answer(ll.get_str("greeting.newbie"), reply_markup = types.InlineKeyboardMarkup(inline_keyboard = buttons))
        await state.set_state(UserDialog.fill_anonymous)

# Handler для сообщения с ответом на вопрос об имени и фамилии
@dp.message(StateFilter(UserDialog.fill_name))
async def fill_name_reply(message: types.Message, state: FSMContext):
    logger.info(f"Realname: {message.text}")
    if(re.search(cyrillic_pattern, message.text) == None):
        await state.update_data(realname = " ".join(message.text.split(" ")[:2]).title())
        await message.reply(ll.get_str("greeting.newbie.form"))
        await message.answer(ll.get_str("greeting.newbie.form.warning"))
        await state.set_state(UserDialog.fill_form)
    else:
        await message.reply(ll.get_str("greeting.newbie.incorrect"))
        await state.set_state(UserDialog.fill_name)

# Handler для сообщения с ответом на вопрос об классе обучения
@dp.message(StateFilter(UserDialog.fill_form))
async def fill_form_reply(message: types.Message, state: FSMContext):
    logger.info(f"Form: {message.text}")
    if(message.text.isdigit() and int(message.text) >= 1 and int(message.text) <= 11):
        await state.update_data(form = int(message.text))
        await message.reply(ll.get_str("greeting.newbie.city"))
        await message.answer(ll.get_str("greeting.newbie.city.warning"))
        await state.set_state(UserDialog.fill_city)
    else:
        await message.reply(ll.get_str("greeting.newbie.incorrect"))
        await state.set_state(UserDialog.fill_form)

# Handler для сообщения с ответом на вопрос о городе обучения
@dp.message(StateFilter(UserDialog.fill_city))
async def fill_city_reply(message: types.Message, state: FSMContext):
    logger.info(f"City: {message.text}")
    if(re.search(cyrillic_pattern, message.text) == None):
        fsm_data = await state.get_data()
        await db.add_entry(
            UserData(
                available = True,
                chat_id = message.from_user.id,
                role = "user",
                rating = 0,
                realname = fsm_data.get("realname"),
                form = fsm_data.get("form"),
                city = message.text.split(" ")[0].upper()
            )
        )
        await message.reply(ll.get_str("greeting.newbie.finish"))
        await state.set_state(UserDialog.ask_question)
    else:
        await message.reply(ll.get_str("greeting.newbie.incorrect"))
        await state.set_state(UserDialog.fill_city)

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
    try:
        await dp.start_polling(bot)
    except Exception as err:
        logger.critical(f"Произошла ошибка при выполнении Bot Polling: {err}")
    await db.close_database()

# Основной код 
if __name__ == "__main__":
    asyncio.run(run_system())