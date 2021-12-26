from aiogram import Dispatcher, types
from database import database as db
from aiogram.dispatcher.filters import Text, IDFilter


base_command = ["/delete"]


async def delete_record(message: types.Message):
    await db.delete_user(message.from_user.id)
    await message.answer(f'Удалена запись о пользователе с id {message.from_user.id}')


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(delete_record, commands="delete")