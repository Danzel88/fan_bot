import logging

from aiogram import Bot, executor
from aiogram.dispatcher import Dispatcher

from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config_reader import load_config
from handlers.event_guest import register_faneron_users_handler
from database import database as db

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/start', description="Описание бота, и подписка на получение информацонных сообщений"),
        BotCommand(command='/check_in', description="Подтвердить посещение"),
    ]
    await bot.set_my_commands(commands)


async def on_shutdown(dp):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.warning("Shutting down..")
    db._conn.close()
    logger.warning("DB Connection closed")


async def on_startup(dp):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    db.connection()
    logger.error('Starting bot')

# Парсинг файла конфигурации
config = load_config("config/bot.ini")
# Объявление и инициализация объектов бота и диспетчера
bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())

# async def main():
#     # Настройка логирования в stdout
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     )
#     logger.error("Starting bot")
#
#     # Парсинг файла конфигурации
#     config = load_config("config/bot.ini")
#     # Объявление и инициализация объектов бота и диспетчера
#     bot = Bot(token=config.tg_bot.token)
#     dp = Dispatcher(bot, storage=MemoryStorage())
#
#
#
#     # Регистрация хэндлеров
#     register_faneron_users_handler(dp, config.tg_bot.admin_id)
#     # register_delayed_checkin(dp)
#
#
#     # Установка команд бота
#     await set_commands(bot)
#
#     # Запуск поллинга
#     # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
#     await dp.start_polling()

if __name__ == '__main__':
    # asyncio.run(main())
    register_faneron_users_handler(dp, config.tg_bot.admin_id)

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
