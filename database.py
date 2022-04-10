import datetime
import os
import sqlite3
import logging
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
        connection = sqlite3.connect(f'{self.name}.db')
        loger.warning('Database created')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE sur_agency(
        id INTEGER PRIMARY KEY,
        company_name VARCHAR(100),
        position VARCHAR(100),
        name VARCHAR(30),
        done_project VARCHAR(100),
        service_list VARCHAR(100),
        manager_name VARCHAR(30),
        rating_manager VARCHAR(4),
        review_us TEXT,
        repeat_chance VARCHAR(25)
        );''')

    def connection(self):
        """Конектимся к БД. Если БД нет - создаем её"""
        db_path = os.path.join(os.getcwd(), f'{self.name}.db')
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f'{self.name}.db')


database = Database(config.tg_bot.db_name)
