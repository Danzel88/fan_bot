import logging
import datetime

from aiogram import executor

from bot import dp, config
from handlers.common import register_handlers_common
from handlers.event_guest import register_faneron_users_handler
from database import database as db
from handlers.sender import register_sender


formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    # TODO раскомментировать на сервере
    filename=f'/log/bot-from-{datetime.datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING)


async def on_shutdown(dp):
    logging.warning("Shutting down..")
    db._conn.close()
    logging.warning("DB Connection closed")


async def on_startup(dp):
    db.connection()
    logging.error('Starting bot')


if __name__ == '__main__':
    register_sender(dp=dp, admin_id=config.tg_bot.admin_id)
    register_faneron_users_handler(dp)
    register_handlers_common(dp)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
