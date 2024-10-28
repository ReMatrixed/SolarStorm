# Подключение встроенных библиотек
import argparse
import logging
import json
import asyncio
import os
import re

# Подключение внутренних модулей
from core.db import DatabaseDispatcher, UserData
from core.locale import LanguageDispatcher

# Подключение модулей библиотеки aiogram для взаимодействия с Telegram Bot API
from aiogram import Dispatcher, Bot, types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage, Redis
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
ll = LanguageDispatcher(
    locale_file_path = "resources/ru/messages.json", 
    censorship_file_path = "resources/ru/censorship.txt",
    logger = logger
)

# Настройка Telegram-бота
fsm_memory_storage = RedisStorage(
    Redis(
        host = cfg.get("redis.host"),
        port = cfg.get("redis.port"),
        password = cfg.get("redis.password")
    )
)
dp = Dispatcher(storage = fsm_memory_storage)
bot = Bot(cfg.get("bot.api_key"), default = DefaultBotProperties(parse_mode = ParseMode.HTML))

# Состояния FSM, предназначенные для общения с пользователем (role: user)
class UserContext(StatesGroup):
    request_form = State() # Запрос номера класса обучения
    request_city = State() # Запрос названия города проживания
    request_optional_data = State() # Запрос на сбор дополнительных данных
    request_realname = State() # Запрос имени и фамилии (необязательно)
    request_question = State() # Запрос вопроса для эксперта
    request_subject = State() # Запрос категории вопроса (школьный предмет)
    request_dialog_permission = State() # Запрос одобрения назначенного системой эксперта
    continue_dialog = State() # Запрос сообщений для передачи эксперту
    finish_dialog = State() # Запрос оценки деятельности эксперта (необязательно)

# Состояния FSM, предназначенные для общения с пользователем (role: member)
class MemberContext(StatesGroup):
    request_dialog_permission = State() # Запрос одобрения вопроса от пользователя
    continue_dialog = State() # Запрос сообщений для передачи пользователю
    finish_dialog = State() # Запрос оценки пользователя (необязательно)

# Паттерн для проверки корректности имени и фамилии
cyrillic_pattern = re.compile(r"[^а-яёА-ЯЁ\s-]|[\s{2,}] ")

# Handler для команды /start
@dp.message(Command("start"))
async def start_bot(message: types.Message, state: FSMContext):
    user_data = await db.get_entry(message.from_user.id)
    if(user_data.available):
        if(user_data.role == "user"):
            await message.answer(ll.get_str("greeting.user").replace("&&1", user_data.realname))
            await state.set_state(UserContext.request_question)
        elif(user_data.role == "member"):
            await message.answer(ll.get_str("greeting.member").replace("&&1", user_data.realname))
            await state.set_state(MemberContext.request_dialog_permission)
    else:
        await message.reply(ll.get_str("greeting.newbie"))
        await message.answer(ll.get_str("greeting.survey.form"))
        await message.answer(ll.get_str("greeting.survey.form.warning"))
        await state.set_state(UserContext.request_form)

# Handler для сообщения с ответом на вопрос об классе обучения (1-й вопрос)
@dp.message(StateFilter(UserContext.request_form))
async def request_form_reply(message: types.Message, state: FSMContext):
    if(message.text.isdigit()): # Проверка на то, является ли ответ пользователя числом
        user_answer = int(message.text) # Преобразование текстового ответа пользователя в число
        if(user_answer >= 1 and user_answer <= 11): # Проверка на валидность значения класса
            await state.update_data(form = user_answer)
            await message.reply(ll.get_str("greeting.survey.city"))
            await message.answer(ll.get_str("greeting.survey.city.warning"))
            await state.set_state(UserContext.request_city)
        else:
            await message.reply(ll.get_str("greeting.survey.incorrect_value"))
    else:
        await message.reply(ll.get_str("greeting.survey.incorrect_value"))

# Handler для сообщения с ответом на вопрос о городе обучения
@dp.message(StateFilter(UserContext.request_city))
async def request_city_reply(message: types.Message, state: FSMContext):
    if(re.search(cyrillic_pattern, message.text) == None): # Проверка на отсутствие запрещённых символов
        await state.update_data(city = message.text.upper()) # Запись преобразованного значения в FSM
        reply_buttons = [
            types.InlineKeyboardButton(text="Да ✅", callback_data="statistics_allow"),
            types.InlineKeyboardButton(text="Нет ❌", callback_data="statistics_disallow")
        ],
        await message.reply(ll.get_str("greeting.survey.optional_data"), reply_markup = types.InlineKeyboardMarkup(inline_keyboard = reply_buttons)) 
        await state.set_state(UserContext.request_optional_data)
    else:
        await message.reply(ll.get_str("greeting.survey.incorrect_value"))

# Callback для ответа на сообщение, касающегося дополнительного опроса
@dp.callback_query(StateFilter(UserContext.request_optional_data), F.data.startswith("statistics_"))
async def request_optional_data_permission(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if(callback.data == "statistics_disallow"):
        available_data = await state.get_data()
        userdata = UserData(
            available = True,
            chat_id = callback.from_user.id, 
            role = "user", 
            rating = 100, 
            realname = "Аноним", 
            form = available_data.get("form"), 
            city = available_data.get("city")
        )
        await db.update_entry(userdata)
        await callback.message.reply(ll.get_str("greeting.survey.finish"))
        await state.set_state(UserContext.request_subject)
    elif(callback.data == "statistics_allow"):
        await callback.message.reply(ll.get_str("greeting.survey.realname"))
        await callback.message.answer(ll.get_str("greeting.survey.realname.warning"))
        await state.set_state(UserContext.request_realname)

# Handler для сообщения с ответом на вопрос об имени и фамилии
@dp.message(StateFilter(UserContext.request_realname))
async def request_realname_reply(message: types.Message, state: FSMContext):
    if(re.search(cyrillic_pattern, message.text) == None):
        await state.update_data(realname = message.text.title())
        available_data = await state.get_data()
        await db.update_entry(
            UserData(
                available = True,
                chat_id = message.from_user.id,
                role = "user",
                rating = 100,
                realname = available_data.get("realname"),
                form = available_data.get("form"),
                city = available_data.get("city")
            )
        )
        await message.reply(ll.get_str("greeting.survey.finish"))
        await state.set_state(UserContext.request_question)
    else:
        await message.reply(ll.get_str("greeting.survey.incorrect_value"))

# Handler для получения текста запроса от пользователя
# Проверки, которые проводятся во время обработки запроса:
# 1. Проверка текста по мат-фильтру (resources/ru/censorship.txt)
@dp.message(StateFilter(UserContext.request_question))
async def request_user_question(message: types.Message, state: FSMContext):
    current_user = await db.get_entry(message.from_user.id)
    if(ll.is_correct(message.text)):
        await message.reply("GOOD")
    else:
        current_user.rating -= 5
        await db.update_entry(current_user)
        await message.reply(ll.get_str("dialog.user.request.bad_language").replace("$$1", str(current_user.rating)))

# Handler для сообщений от пользователя, которые были отправлены во время диалога с экспертом
@dp.message(StateFilter(UserContext.continue_dialog))
async def continue_user_dialog(message: types.Message, state: FSMContext):
    pass

# Handler для сообщений от эксперта, которые были отправлены во время диалога с экспертом
@dp.message(StateFilter(MemberContext.continue_dialog))
async def continue_member_dialog(message: types.Message, state: FSMContext):
    pass

async def run_system():
    await db.setup(
        host = cfg.get("db.host"),
        port = cfg.get("db.port"),
        username = cfg.get("db.username"),
        password = cfg.get("db.password"),
        dbname = cfg.get("db.name"),
        logger = logger
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