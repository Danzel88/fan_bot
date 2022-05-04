from aiogram import executor

from bot import dp, config
from handlers.common import register_handlers_common
from handlers.event_guest import register_sur_client_handler
from database import database as db
from handlers.sender import register_sender

from config.loger import loger


async def on_shutdown(dp):
    loger.warning("Shutting down..")
    db._conn.close()
    loger.warning("DB Connection closed")


async def on_startup(dp):
    db.connection()
    loger.error('Starting bot')


if __name__ == '__main__':
    register_sender(dp=dp, admin_id=config.tg_bot.admin_id)
    register_sur_client_handler(dp)
    register_handlers_common(dp)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
