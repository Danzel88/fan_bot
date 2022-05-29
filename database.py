import os
import sqlite3
from config.loger import loger
from config_reader import load_config


configs = load_config("config/bot.ini")
faneron_users_create = '''CREATE TABLE faneron_users(
        id INTEGER PRIMARY KEY,
        presence VARCHAR(25),
        event_place VARCHAR(12),
        age VARCHAR(5),
        city VARCHAR (7),
        review TEXT,
        tg_id INTEGER UNIQUE
        );'''
mailing_users_create = '''CREATE TABLE users_for_mailing(
        id INTEGER PRIMARY KEY,
        tg_id INTEGER UNIQUE
        );'''

class Database:
    def __init__(self, name=None):
        self.name = name
        self._conn = self.connection()
        loger.warning(f"Database connection {self.name} established")

    def create_db(self):
        """Создаем базу"""
        connection = sqlite3.connect(self.name)
        loger.warning('Database created')
        cursor = connection.cursor()
        cursor.execute(faneron_users_create)
        cursor.execute(mailing_users_create)

    def connection(self):
        """Конектимся к БД. Если БД нет - создаем её"""
        database_path = os.path.join(os.getcwd(), self.name)
        if not os.path.exists(database_path):
            self.create_db()
        return sqlite3.connect(self.name)

    async def _execute_query(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def _execute_query2(self, query, val, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query, val)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def create_user(self, tg_id: int):
        try:
            insert_query = '''INSERT INTO users_for_mailing (tg_id) VALUES (?)'''
            val = (tg_id,)
            await self.execute_update(insert_query, val)
            loger.warning(f"user {tg_id} added to mailing_db")
        except Exception:
            loger.warning(f"User try restart bot, but user "
                          f"{tg_id} already exists in mailing list")

    async def select_user(self, tg_id: int):
        select_query = f'''SELECT * FROM faneron_users WHERE tg_id = {tg_id}'''
        record = await self._execute_query(select_query, select=True)
        return record

    async def get_all_users(self):
        get_query = f'''SELECT tg_id FROM users_for_mailing;'''
        cursor = self._conn.cursor()
        all_users = cursor.execute(get_query).fetchall()
        return all_users

    async def execute_update(self, query, val):
        cur = self._conn.cursor()
        cur.execute(query, val)
        self._conn.commit()
        cur.close()

    async def update_user(self, presence: str = None, event_place: str = None,
                          age: str = None, city: str = None, review: str = None, tg_id: int = None):
        update_query = '''UPDATE faneron_users SET presence = ?, event_place = ?, age = ?, city = ?, review = ? WHERE tg_id = ?'''
        val = (presence, event_place, age, city, review, tg_id)
        await self.execute_update(update_query, val)
        if review:
            loger.warning(f'user with {tg_id} add review')
        else:
            loger.warning(f"user with {tg_id} updated status {presence}")

    async def writer(self, data: dict):
        val = (data["presence"], data["event_place"],
               data["age"], data["city"],
               data["review"], int(data["tg_id"]),)
        create_query = '''INSERT into faneron_users (presence, event_place, 
        age, city, review, tg_id) VALUES (?,?,?,?,?,?)'''
        if await self.select_user(data["tg_id"]):
            update_query = '''UPDATE faneron_users SET presence = ?, event_place = ?, age = ?, city = ?, review = ? WHERE tg_id = ?'''
            await self._execute_query2(update_query, val)
            return
        await self._execute_query2(create_query, val)


database = Database(configs.tg_bot.db_path)
mailing_database = Database(configs.tg_bot.mailing_db_path)
