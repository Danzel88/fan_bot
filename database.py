import os
import sqlite3
from config_reader import load_config
from config.loger import loger

config = load_config("config/bot.ini")


class Database:
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        loger.warning("Database connection established")

    def create_db(self):
        """Создаем базу"""
        connection = sqlite3.connect(self.name)
        loger.warning('Database created')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE sur_agency(
        id INTEGER PRIMARY KEY,
        tg_id INTEGER,
        client_state VARCHAR(30),
        client_info VARCHAR(200),
        manager_name VARCHAR(30),
        managers_rating VARCHAR(4),
        review_text TEXT,
        return_probability VARCHAR(50)
        );''')

    def connection(self):
        """Конектимся к БД. Если БД нет - создаем её"""
        db_path = os.path.join(os.getcwd(), self.name)
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(self.name)

    def _execute_query(self, query, val, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query, val)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    def writer(self, data: dict):
        val = (int(data["tg_id"]), data["client_state"], data["client_info"],
               data["manager_name"], data["managers_rating"],
               data["review_text"], data["return_probability"],)
        create_query = '''INSERT into sur_agency (tg_id, client_state, client_info, manager_name, managers_rating, review_text, return_probability) VALUES (?,?,?,?,?,?,?)'''
        self._execute_query(create_query, val)

    def select_user(self, tg_id):
        select_query = '''SELECT tg_id FROM sur_agency WHERE tg_id=?'''
        val = (tg_id, )
        user = self._execute_query(select_query, val, select=True)
        return user

    def get_all_client(self):
        select_query = '''SELECT * from sur_agency'''
        cursor = self._conn.cursor()
        all_client = cursor.execute(select_query)
        return all_client


database = Database(config.tg_bot.db_path)
