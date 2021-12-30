import datetime
import os
import sqlite3
import logging
from config_reader import load_config
import pandas as pd


config = load_config("config/bot.ini")
formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'bot-from-{datetime.datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING)


class Database:
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.warning("Database connection established")

    def create_db(self):
        connection = sqlite3.connect(f'{self.name}.db')
        logging.warning('Database created')
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

    async def create_user(self, tg_id: int):
        insert_query = f"INSERT INTO faneron_users (tg_id) VALUES ({tg_id})"
        await self._execute_query(insert_query)
        logging.warning(f"user {tg_id} added to DB")

    async def select_user(self, tg_id: int):
        select_query = f'SELECT * FROM faneron_users WHERE tg_id = {tg_id}'
        record = await self._execute_query(select_query, select=True)
        return record

    async def get_all_users(self):
        get_query = f'SELECT tg_id FROM faneron_users;'
        cursor = self._conn.cursor()
        all_users = cursor.execute(get_query).fetchall()
        return all_users

    async def create_or_update_user(self, presence: str = None, tg_id: int = None):
        user_presence = await self.select_user(tg_id)
        if user_presence is not None:
            await self.update_user(presence=presence, tg_id=tg_id)
        else:
            await self.create_user(tg_id=tg_id)

    async def update_user(self, presence: str = None, person_role: str = None,
                          age: str = None, city: str = None, review: str = None, tg_id: int = None):
        update_query = f'UPDATE faneron_users SET presence = "{presence}",' \
                       f'person_role = "{person_role}", age = "{age}", city = "{city}",' \
                       f'review = "{review}" WHERE tg_id = {tg_id}'
        await self._execute_query(update_query)
        if review:
            logging.warning(f'user with {tg_id} add review')
        else:
            logging.warning(f"user with {tg_id} updated status to {presence}")

    async def subscribe(self, presence: str, tg_id: int):
        subscribe_query = f"UPDATE faneron_users SET presence = '{presence}' WHERE tg_id = {tg_id}"
        await self._execute_query(subscribe_query)
        logging.warning(f"user with {tg_id} subscribe to the newsletter")

    async def delete_user(self, tg_id: int):
        delete_query = f"DELETE FROM faneron_users WHERE tg_id = {tg_id}"
        await self._execute_query(delete_query)
        logging.warning(f"user with {tg_id} deleted")


database = Database(config.tg_bot.db_name)
