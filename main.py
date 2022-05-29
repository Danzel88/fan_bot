from aiogram import executor

from bot import dp, config
from handlers.common import register_handlers_common
from handlers.event_guest import register_faneron_users_handler
from config.loger import loger
from database import database, mailing_database
from handlers.sender import register_sender


async def on_shutdown(dp):
    loger.warning("Shutting down..")
    database._conn.close()
    mailing_database._conn.close()
    await dp.storage.close()
    await dp.storage.wait_closed()
    loger.warning("DB Connection closed")


async def on_startup(dp):
    database.connection()
    mailing_database.connection()
    loger.error('Starting bot')


if __name__ == '__main__':
    register_sender(dp=dp, admin_id=config.tg_bot.admin_id)
    register_faneron_users_handler(dp)
    register_handlers_common(dp)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
