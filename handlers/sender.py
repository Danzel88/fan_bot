import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.utils import exceptions
from aiogram.dispatcher.filters import IDFilter

from database import database as db


log = logging.getLogger("broadcast")


async def init_sender_state(message: types.Message):
    await message.answer(f'Это функция рассылки. Сообщения будут отправлены всем пользователям бота. '
                         f'Пришли сообщение, которое нужно разослать', reply_markup=types.ReplyKeyboardRemove())


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(bot, user_id, text)
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def start_spam(message: types.Message):
    all_users = await db.get_all_users()
    users_list = list(zip(*all_users))
    count = 0
    print(count)
    try:
        for user_id in users_list:
            print(user_id)
            if await send_message(user_id=user_id, text=message.text):
                count += 1
            await asyncio.sleep(.05)
    finally:
        log.info(f"{count} отправлено")


def register_sender(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(init_sender_state, IDFilter(user_id=admin_id), commands="sender")
    dp.register_message_handler(start_spam, IDFilter(user_id=admin_id))
