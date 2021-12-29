import asyncio
import logging
import datetime

from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import exceptions
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config_reader import load_config
from dialogs import msg
from handlers.common import register_handlers_common
from handlers.event_guest import register_faneron_users_handler
from database import database as db

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'

# logging.basicConfig(
#     # TODO раскомментировать на сервере
#     filename=f'bot-from-{datetime.datetime.now().date()}.log',
#     filemode='w',
#     format=formatter,
#     datefmt='%Y-%m-%d %H:%M:%S',
#     # TODO logging.WARNING
#     level=logging.WARNING
# )


# logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/start', description="Описание бота, и подписка на получение информацонных сообщений"),
        BotCommand(command='/delete', description="Команда для тестирования. Удалить запись о себе"),
        BotCommand(command='/sender', description="Рассылка, только для админа")
    ]
    await bot.set_my_commands(commands)


async def on_shutdown(dp):
    logging.warning("Shutting down..")
    db._conn.close()
    logging.warning("DB Connection closed")


async def on_startup(dp):
    db.connection()
    logging.error('Starting bot')


config = load_config("config/bot.ini")
bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())
log = logging.getLogger("broadcast")


class Sender(StatesGroup):
    waiting_init_admin = State()
    waiting_message_from_admin = State()
    waiting_message_from_admin_to_test_mailing = State()


async def init_sender_state(message: types.Message):
    if message.text == "/test_sender":
        await message.answer(f'{msg.message_for_test_sender}', parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
        await Sender.waiting_message_from_admin_to_test_mailing.set()
        return
    await message.answer(f'{msg.message_for_sender}', parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    await Sender.waiting_message_from_admin.set()


async def send_message(message: types.Message,
                       user_id: int, disable_notification: bool = False) -> bool:
    try:
        if message.text is not None:
            await bot.send_message(chat_id=user_id, text=message.text, disable_notification=disable_notification,
                                   parse_mode="HTML")
        elif message.photo is not None:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption,
                                 disable_notification=disable_notification, parse_mode="HTML")
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id=user_id, message=message)
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.warning(f"Target [ID:{user_id}]: failed")
    else:
        logging.warning(f"Target [ID:{user_id}]: success")
        # await Sender.waiting_init_admin.set()
        return True
    return False


async def test_sender(message: types.Message, state: FSMContext):
    try:
        await send_message(user_id=config.tg_bot.admin_id, message=message)
        logging.warning(f'Start test mailing')
    except IndexError:
        logging.error(f'нет пользователей для отправки')
    finally:
        await state.finish()


async def start_spam(message: types.Message, state: FSMContext):
    all_users = await db.get_all_users()
    users_list = tuple(zip(*all_users))
    count = 0
    try:
        for user_id in users_list[0]:
            if await send_message(user_id=user_id, message=message):
                count += 1
            await asyncio.sleep(.05)
    except IndexError:
        logging.error(f'нет пользователей для отправки')
    finally:
        await state.finish()
        logging.warning(f'{count} сообщений отправлено')


def register_sender(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(init_sender_state, IDFilter(user_id=admin_id), commands="sender", state="*")
    dp.register_message_handler(init_sender_state, IDFilter(user_id=admin_id), commands="test_sender", state="*")
    dp.register_message_handler(start_spam, IDFilter(user_id=admin_id), state=Sender.waiting_message_from_admin,
                                content_types=['text', 'photo'])
    dp.register_message_handler(test_sender, IDFilter(user_id=admin_id),
                                state=Sender.waiting_message_from_admin_to_test_mailing,
                                content_types=['text', 'photo'])

if __name__ == '__main__':
    register_sender(dp=dp, admin_id=config.tg_bot.admin_id)
    register_faneron_users_handler(dp)
    register_handlers_common(dp)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
