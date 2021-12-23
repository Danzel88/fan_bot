from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup

presence = ["посетил", "подписаться на новости"]
person_role = ["спикер", "гость", "организатор"]
age_interval = ["16-20", "21-25", "26-30", "31-35", "36-40", "40-50", "50+"]
city = ["москва", "другой"]


class FaneronUsers(StatesGroup):
    init_state = State()
    waiting_for_presence_accept = State()
    waiting_for_role = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_review = State()


async def init_user(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for pres in presence:
        keyboard.add(pres)
    await message.answer(f"Уже был на мероприятии?", reply_markup=keyboard)
    await FaneronUsers.init_state.set()


async def delayed_registration(message: types.Message, state: FSMContext):
    if message.text.lower() not in presence:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(presence=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for role in person_role:
        keyboard.add(role)
    await FaneronUsers.next()

    await message.answer(f"В качестве кого был на мероприятии", reply_markup=keyboard)


async def pres_accept(message: types.Message, state: FSMContext):
    if message.text.lower() not in presence:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    elif message.text.lower() == "подписаться на новости":
        await message.answer(f'Для того что бы оставить отзыв после посещения отправь команду (/check_in)')
        await FaneronUsers.init_state.set()
        return
    await state.update_data(presence=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for role in person_role:
        keyboard.add(role)
    await FaneronUsers.next()

    await message.answer(f"В качестве кого был на мероприятии", reply_markup=keyboard)


async def role_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in person_role:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(role=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for age in age_interval:
        keyboard.add(age)
    await FaneronUsers.next()
    await message.answer(f"Сколько тебе лет?", reply_markup=keyboard)


async def age_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in age_interval:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(age=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in city:
        keyboard.add(c)
    await FaneronUsers.next()
    await message.answer(f"Ты из москвы или из лругого города", reply_markup=keyboard)


async def city_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in city:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(city=message.text.lower())
    await FaneronUsers.next()
    await message.answer(f'черкани пару строк про эвент.', reply_markup=types.ReplyKeyboardRemove())


async def get_review(message: types.Message, state: FSMContext):
    await state.update_data(review=message.text)
    await state.update_data(tg_id=message.from_user.id)
    user_data = await state.get_data()
    await message.answer(f"Спасибо за комменты")
    await state.finish()


def register_faneron_users_handler(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(init_user, commands='start', state='*')
    dp.register_message_handler(pres_accept, state=FaneronUsers.init_state)
    dp.register_message_handler(role_chosen, state=FaneronUsers.waiting_for_presence_accept)
    dp.register_message_handler(age_chosen, state=FaneronUsers.waiting_for_role)
    dp.register_message_handler(city_chosen, state=FaneronUsers.waiting_for_age)
    dp.register_message_handler(get_review, state=FaneronUsers.waiting_for_city)


def register_delayed_checkin(dp: Dispatcher):
    dp.register_message_handler(delayed_registration, command='check', state=FaneronUsers.init_state)


