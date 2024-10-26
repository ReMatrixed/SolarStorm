# Подключение библиотеки для работы с СУБД PostgreSQL
import psycopg

# Подключение библиотеки для создания классов данных
from dataclasses import dataclass

# Подключение библиотеки логгирования
import logging

# Информация об одном пользователе
@dataclass
class UserData:
    is_member: bool
    rating: int
    realname: str
    form: int
    school: str

class DatabaseDispatcher:
    # Экземпляр подключения к базе данных
    connection: psycopg.Connection
    logger: logging.Logger
    is_connected = False

    def __init__(self, host: str, port: int, username: str, password: str, dbname: str, logger: logging.Logger):
        self.logger = logger
        self.logger.info("Подключение к базе данных...")
        self.connection = psycopg.connect(
            f"hostaddr={host} port={port} dbname={dbname} user={username} password={password}"
        )
        self.logger.info("База данных подключена.")
        self.is_connected = True

    def __del__(self):
        if(self.is_connected):
            self.close_database()

    # Структура базы данных пользователей:
    # ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ
    # 1-й столбец (id) - идентификационный номер, создается по умолчанию
    # 2-й столбец (chat_id) - Telegram ChatID, будет получен от пользователя, если он обратится к боту
    # 3-й столбец (role) - тип пользователя (user, member или admin)
    # 4-й столбец (rating) - рейтинг пользователя (целое число в диапазоне от 0 до 1000)
    # ОПЦИОНАЛЬНЫЕ ДАННЫЕ
    # 5-й столбец (realname) - фамилия и имя пользователя, могут быть получены от пользователя, если он укажет их
    # 6-й столбец (form) - номер класса, в котором обучается пользователь (целое число от 1 до 11)
    # 7-й столбец (school) - название школы, в которой обучается пользователь

    # Структура базы данных участников чат-центра:
    # ВСЕ ДАННЫЕ ОБЯЗАТЕЛЬНЫ
    # 1-й столбец (id) - идентификационный номер, создается по умолчанию
    # 2-й столбец (chat_id) - Telegram ChatID, будет получен от участника, когда он обратится к боту
    # 3-й столбец (answers) - кол-во успешных ответов на вопросы учеников
    # 4-й столбец (images) - кол-во изображений, отправленных участниками
    # 5-й столбец (videos) - кол-во видеоматериалов, отправленных участниками
    # 6-й столбец (status) - статус участника (AVAILABLE - доступен, WORKING - работает над запросом, PAUSED - временно недоступен, FIRED - покинул чат-центр)
    def prepare_database(self):
        with self.connection.cursor() as cur: 
            self.logger.info("Подготовка базы данных...")
            self.logger.info("Подготовка таблицы users...")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    role TEXT NOT NULL,
                    rating SMALLINT NOT NULL,
                    realname TEXT NOT NULL,
                    form SMALLINT NOT NULL,
                    school TEXT NOT NULL
                );
                """
            )
            self.logger.info("Подготовка таблицы members...")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    answers INTEGER NOT NULL,
                    images INTEGER NOT NULL,
                    videos INTEGER NOT NULL,
                    status TEXT NOT NULL
                );
                """
            )
            self.logger.info("Применение изменений в базе данных...")
            self.connection.commit()
            self.logger.info("База данных готова.")

    def close_database(self):
        self.logger.info("Отключение от базы данных...")
        self.connection.close() 
        self.is_connected = False
        self.logger.info("База данных отключена.")

    def get_entries(self, chat_id: int):
        with self.connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
            return cur.fetchall()

    def destroy_database(self):
        with self.connection.cursor() as cur:
            cur.execute("DROP TABLE users, members")
            self.connection.commit()