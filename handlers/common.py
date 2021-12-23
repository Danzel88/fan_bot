from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


base_command = ["/check_in", "/registration"]


async def cmd_start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in base_command:
        keyboard.add(cmd)
    await state.finish()
    await message.answer(f"Если ты уже посетил мероприятие, отправь команду (/check_in) пройди небольшой опрос "
                         f"и оставь свой отзыв. Если еще не посетил но хочешь получать новости отправь команду "
                         f"(/registration)",
                         reply_markup=keyboard)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")