import datetime
import os
import sqlite3
# import logging
from config.loger import loger
from config_reader import load_config


config = load_config("config/bot.ini")
# formatter = '[%(asctime)s] %(levelname)8s --- %(message)s ' \
#             '(%(filename)s:%(lineno)s)'
# logging.basicConfig(
#     filename=f'log/bot-from-'
#              f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
#     filemode='w',
#     format=formatter,
#     datefmt='%Y-%m-%d %H:%M:%S',
#     level=logging.WARNING)


class Database:
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        loger.warning("Database connection established")

    def create_db(self):
        """Создаем базу"""
        connection = sqlite3.connect(f'{self.name}.db')
        loger.warning('Database created')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE faneron_users(
        id INTEGER PRIMARY KEY,
        presence VARCHAR(25),
        person_role VARCHAR(12),
        age VARCHAR(5),
        city VARCHAR (7),
        review TEXT,
        tg_id INTEGER UNIQUE
        );''')

    def connection(self):
        """Конектимся к БД. Если БД нет - создаем её"""
        db_path = os.path.join(os.getcwd(), f'{self.name}.db')
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f'{self.name}.db')

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

    async def create_user(self, presence:str, tg_id: int):
        insert_query = '''INSERT INTO faneron_users (presence, tg_id) VALUES (?,?)'''
        val = (presence, tg_id,)
        await self.execute_update(insert_query, val)
        loger.warning(f"user {tg_id} added to DB")

    async def select_user(self, tg_id: int):
        select_query = f'''SELECT * FROM faneron_users WHERE tg_id = {tg_id}'''
        record = await self._execute_query(select_query, select=True)
        return record

    async def get_all_users(self):
        get_query = f'''SELECT tg_id FROM faneron_users;'''
        cursor = self._conn.cursor()
        all_users = cursor.execute(get_query).fetchall()
        return all_users

    #старая реализация метода обновления записи с пользователем в бд
    #проверить связаность и удалить при рефакторинге
    # async def create_or_update_user(self, presence: str = None,
    #                                 tg_id: int = None):
    #     user_presence = await self.select_user(tg_id)
    #     if user_presence is not None:
    #         await self.update_user(presence=presence, tg_id=tg_id)
    #     else:
    #         await self.create_user(tg_id=tg_id)

    async def execute_update(self, query, val):
        cur = self._conn.cursor()
        cur.execute(query, val)
        self._conn.commit()
        cur.close()

    async def update_user(self, presence: str = None, person_role: str = None,
                          age: str = None, city: str = None, review: str = None, tg_id: int = None):
        update_query = '''UPDATE faneron_users SET presence = ?, person_role = ?, age = ?, city = ?, review = ? WHERE tg_id = ?'''
        val = (presence, person_role, age, city, review, tg_id)
        await self.execute_update(update_query, val)
        if review:
            loger.warning(f'user with {tg_id} add review')
        else:
            loger.warning(f"user with {tg_id} updated status {presence}")

    async def writer(self, data: dict):
        val = (data["presence"], data["role"],
               data["age"], data["city"],
               data["review"], int(data["tg_id"]),)
        create_query = '''INSERT into faneron_users (presence, person_role, 
        age, city, review, tg_id) VALUES (?,?,?,?,?,?)'''
        if await self.select_user(data["tg_id"]):
            update_query = '''UPDATE faneron_users SET presence = ?, person_role = ?, age = ?, city = ?, review = ? WHERE tg_id = ?'''
            await self._execute_query2(update_query, val)
            return
        await self._execute_query2(create_query, val)

database = Database(config.tg_bot.db_name)
