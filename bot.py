from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config_reader import load_config

storage = RedisStorage2('localhost',
                        6379,
                        db=6,
                        pool_size=10,
                        prefix='faneron_user')

config = load_config("config/bot.ini")
bot = Bot(token=config.tg_bot.token)
# dp = Dispatcher(bot, storage=MemoryStorage())
dp = Dispatcher(bot, storage=storage)
