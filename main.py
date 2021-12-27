import asyncio
import logging

from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import exceptions
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config_reader import load_config
from handlers.common import register_handlers_common
from handlers.event_guest import register_faneron_users_handler
from database import database as db


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/start', description="Описание бота, и подписка на получение информацонных сообщений"),
        BotCommand(command='/delete', description="Команда для тестирования. Удалить запись о себе"),
        BotCommand(command='/sender', description="Рассылка, только для админа")
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


config = load_config("config/bot.ini")
bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())
log = logging.getLogger("broadcast")


class Sender(StatesGroup):
    waiting_init_admin = State()
    waiting_message_from_admin = State()


async def init_sender_state(message: types.Message):
    await message.answer(f'Это функция рассылки. Сообщения будут отправлены всем пользователям бота. '
                         f'Пришли сообщение, которое нужно разослать', reply_markup=types.ReplyKeyboardRemove())
    await Sender.waiting_message_from_admin.set()


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        logger.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logger.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logger.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(bot, user_id, text)
    except exceptions.UserDeactivated:
        logger.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logger.warning(f"Target [ID:{user_id}]: failed")
    else:
        logger.warning(f"Target [ID:{user_id}]: success")
        await Sender.waiting_init_admin.set()
        return True
    return False


async def start_spam(message: types.Message):
    all_users = await db.get_all_users()
    users_list = tuple(zip(*all_users))
    count = 0
    try:
        for user_id in users_list[0]:
            if await send_message(user_id=user_id, text=message.text):
                count += 1
            await asyncio.sleep(.05)
    finally:
        logger.warning(f'{count} сообщений отправлено')


def register_sender(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(init_sender_state, IDFilter(user_id=admin_id), commands="sender", state="*")
    dp.register_message_handler(start_spam, IDFilter(user_id=admin_id), state=Sender.waiting_message_from_admin)


if __name__ == '__main__':
    register_faneron_users_handler(dp)
    register_handlers_common(dp)
    register_sender(dp=dp, admin_id=config.tg_bot.admin_id)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
