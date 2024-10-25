# Подключение библиотеки для работы с SQLite
import sqlite3
# Подключение библиотеки для создания классов данных
from dataclasses import dataclass
# Подключение библиотеки логгирования
from core.logger import internal_log

# Информация об 1-м пользователе
@dataclass
class UserData:
    is_member: bool
    rating: int
    realname: str
    form: int
    school: str

# Подключение базы данных пользователей
internal_log.info("Создание базы данных...")
main_db_connection = sqlite3.connect("db/users.db")
main_db_cursor = main_db_connection.cursor

# Структура базы данных пользователей:
# ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ
# 1-й столбец (id) - идентификационный номер, создается по умолчанию
# 2-й столбец (chat_id) - Telegram Chat-ID, будет получен от пользователя, если он обратится к боту
# 3-й столбец (role) - тип пользователя (user, member или admin)
# 4-й столбец (rating) - рейтинг пользователя (целое число в диапазоне от 0 до 1000)
# ОПЦИОНАЛЬНЫЕ ДАННЫЕ
# 5-й столбец (realname) - фамилия и имя пользователя, могут быть получены от пользователя, если он укажет их
# 6-й столбец (form) - номер класса, в котором обучается пользователь (целое число от 1 до 11)
# 7-й столбец (school) - название школы, в которой обучается пользователь

# Структура базы данных участников чат-центра:
# ВСЕ ДАННЫЕ ОБЯЗАТЕЛЬНЫ
# 1-й столбец (id) - идентификационный номер, создается по умолчанию
# 2-й столбец (chat_id) - Telegram Chat-ID, будет получен от участника, когда он обратится к боту
# 3-й столбец (answers) - кол-во успешных ответов на вопросы
# 4-й столбец (images) - кол-во изображений, отправленных участниками
# 5-й столбец (videos) - кол-во видеоматериалов, отправленных участниками
# 6-й столбец (status) - статус участника (ACTIVE - работает, PAUSED - временно недоступен, FIRED - покинул чат-центр)
async def prepare_database():
    internal_log.info("Подготовка базы данных...")
    await main_db_cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            rating INTEGER NOT NULL,
            realname TEXT NOT NULL,
            form NUMBER NOT NULL,
            school TEXT NOT NULL
        )
        '''
    )
    await main_db_cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Members (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            answers INTEGER NOT NULL,
            images INTEGER NOT NULL,
            videos INTEGER NOT NULL,
            status TEXT NOT NULL
        )
        '''
    )

async def get_user_data(chat_id: int):
    pass