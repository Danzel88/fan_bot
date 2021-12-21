from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup

presence = ["Был", "Не был"]
person_role = ["Спикер", "Гость", "Организатор"]
age_interval = ["16-20", "21-25", "26-30", "31-35", "36-40", "40-50", "50+"]
city = ["Москва", "Другой"]


class FaneronUsers(StatesGroup):
    waiting_for_presence_accept = State()
    waiting_for_role = State()
    waiting_for_age = State()
    waiting_for_city = State()


async def users_statistic_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for pres in presence:
        keyboard.add(pres)
    await message.answer(f"Ты уже посетил Фанерон", reply_markup=keyboard)
    await FaneronUsers.waiting_for_presence_accept.set()


async def role_choose(message: types.Message, state: FSMContext):
    if message.text.lower() not in presence:
        await message.answer(f"Выбери из предложенных вариантов 'был'/'не был'")
        return
    await state.update_data(persone_role=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for role in person_role:
        keyboard.add(role)
    await FaneronUsers.next()
    await message.answer(f"В качестве кого посетиль мероприятие?", reply_markup=keyboard)


async def age_choose(message: types.Message, state: FSMContext):
    if message.text.lower() not in person_role:
        await message.answer(f"Выбери из предложенных вариантов посетителя")
        return
    await state.update_data(age=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for age in age_interval:
        keyboard.add(age)
    await FaneronUsers.next()
    await message.answer(f"Сколько тебе лет", reply_markup=keyboard)


async def city_choose(message: types.Message, state: FSMContext):
    if message.text.lower() not in age_interval:
        await message.answer(f"Выбери из предложенных вариантов интервалов возраста")
        return
    await state.update_data(city=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in city:
        keyboard.add(c)
    await FaneronUsers.next()
    await message.answer(f"Ты из Москвы или из другого города?")

async def get_user_data(message: types.Message, state: FSMContext):
    if message.text.lower() not in city:
        await message.answer(f"Выбери из предложенных вариантов интервалов городов")
        return
    user_data = await state.get_data()
    await message.answer(f"Ваш стэйт:{user_data}")
    await state.finish()


async def secret_command(message: types.Message):
    await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_faneron_users_handler(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(users_statistic_start, commands='start', state='*')
    dp.register_message_handler(role_choose, commands="role", state=FaneronUsers.waiting_for_presence_accept)
    dp.register_message_handler(age_choose, state=FaneronUsers.waiting_for_role)
    dp.register_message_handler(city_choose, state=FaneronUsers.waiting_for_age)
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands="332199")
