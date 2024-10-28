# Подключение библиотеки для работы с СУБД PostgreSQL
import psycopg

# Подключение библиотеки для создания классов данных
from dataclasses import dataclass

# Подключение библиотеки логгирования
import logging

# Информация об одном пользователе
@dataclass
class UserData:
    available: bool = False
    chat_id: int = 0
    role: str = "user"
    rating: int = -1
    realname: str = "НЕИЗВЕСТНО"
    form: int = -1
    city: str = "НЕИЗВЕСТЕН"

# Основной класс управления БД
class DatabaseDispatcher:
    # Экземпляр подключения к базе данных
    connection: psycopg.Connection
    logger: logging.Logger
    is_connected = False

    async def setup(self, host: str, port: int, username: str, password: str, dbname: str, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.info("Подключение к базе данных...")
        self.connection = await psycopg.AsyncConnection.connect(
            f"hostaddr={host} port={port} dbname={dbname} user={username} password={password}"
        )
        self.logger.info("База данных подключена.")
        self.is_connected = True

    # Структура базы данных пользователей:
    # ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ
    # 1-й столбец (id) - идентификационный номер, создается по умолчанию
    # 2-й столбец (chat_id) - Telegram ChatID, будет получен от пользователя, если он обратится к боту
    # 3-й столбец (role) - тип пользователя (user, member или admin)
    # 4-й столбец (rating) - рейтинг пользователя (целое число в диапазоне от 0 до 1000)
    # ОПЦИОНАЛЬНЫЕ ДАННЫЕ
    # 5-й столбец (realname) - фамилия и имя пользователя, могут быть получены от пользователя, если он укажет их
    # 6-й столбец (form) - номер класса, в котором обучается пользователь (целое число от 1 до 11)
    # 7-й столбец (city) - название города, в котором обучается/проживает пользователь

    # Структура базы данных участников чат-центра:
    # ВСЕ ДАННЫЕ ОБЯЗАТЕЛЬНЫ
    # 1-й столбец (id) - идентификационный номер, создается по умолчанию
    # 2-й столбец (chat_id) - Telegram ChatID, будет получен от участника, когда он обратится к боту
    # 3-й столбец (subject) - предмет, на вопросы которого отвечает участник (математика, физика, информатика и т.д.)
    # 4-й столбец (answers) - кол-во успешных ответов на вопросы учеников
    # 5-й столбец (images) - кол-во изображений, отправленных участниками
    # 6-й столбец (videos) - кол-во видеоматериалов, отправленных участниками
    # 7-й столбец (status) - статус участника (AVAILABLE - доступен, WORKING - работает над запросом, PAUSED - временно недоступен, FIRED - покинул чат-центр)

    # Структура базы данных запросов
    # 1-й столбец (id) - идентификационный номер, создается по умолчанию
    # 2-й столбец (chat_id) - Telegram ChatID, будет получен от Пользователя
    # 3-й столбец (subject) - предмет, по которому задается вопрос
    # 4-й столбец (priority) - приоритет запроса, вычисляется при его создании
    # 5-й столбец (question) - текст запроса (вопрос от Пользователя)
    # 6-й столбец (status) - статус запроса (APPROVED - выполняется, PENDING - ожидает принятия, CANCELED - отменен)
    # 7-й столбец (employee) - chat_id участника, принявшего запрос
    async def prepare_database(self) -> None:
        async with self.connection.cursor() as cur: 
            self.logger.info("Подготовка базы данных...")
            self.logger.info("Подготовка таблицы users...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    rating SMALLINT NOT NULL,
                    realname TEXT NOT NULL,
                    form SMALLINT NOT NULL,
                    city TEXT NOT NULL
                );
                """
            )
            await cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS chat_id_index ON users (chat_id)")

            self.logger.info("Подготовка таблицы members...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    subject TEXT NOT NULL,
                    answers INTEGER NOT NULL,
                    images INTEGER NOT NULL,
                    videos INTEGER NOT NULL,
                    status TEXT NOT NULL
                );
                """
            )
            await cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS chat_id_index ON members (chat_id)")

            self.logger.info("Подготовка таблицы tasks...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    subject TEXT NOT NULL,
                    priority SMALLINT NOT NULL,
                    question TEXT NOT NULL,
                    status TEXT NOT NULL,
                    employee BIGINT
                )
                """
            )
            await cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS chat_id_index ON tasks (chat_id)")

            self.logger.info("Применение подготовительных изменений в базе данных...")
            await self.connection.commit()
            self.logger.info("База данных готова.")

    # Получить запись в базе данных, chat_id которой соответствует переданному значению
    async def get_entry(self, chat_id: int) -> UserData:
        async with self.connection.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
            available_data = await cur.fetchone()
            if(available_data != None):
                return UserData(
                    available = True,
                    chat_id = available_data[1],
                    role = available_data[2],
                    rating = available_data[3],
                    realname = available_data[4],
                    form = available_data[5],
                    city = available_data[6]
                )
            else:
                return UserData(available = False)
        
    # Добавить/изменить запись в базе данных, информация передается в качестве dataclass'а UserData
    async def update_entry(self, userdata: UserData) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users (chat_id, role, rating, realname, form, city) VALUES (%s, %s, %s, %s, %s, %s) 
                ON CONFLICT (chat_id) DO UPDATE SET 
                    role = EXCLUDED.role,
                    rating = EXCLUDED.rating,
                    realname = EXCLUDED.realname,
                    form = EXCLUDED.form,
                    city = EXCLUDED.city
                """, 
                (userdata.chat_id, userdata.role, userdata.rating, userdata.realname, userdata.form, userdata.city)
            )
            await self.connection.commit()

    # Проверить, существует ли запись в базе данных по chat_id
    async def is_entry_exists(self, chat_id: int) -> bool:
        if(await self.get_entry(chat_id) == None):
            return False
        else:
            return True
        
    # Отключить базу данных    
    async def close_database(self) -> None:
        self.logger.info("Отключение от базы данных...")
        await self.connection.close() 
        self.is_connected = False
        self.logger.info("База данных отключена.")