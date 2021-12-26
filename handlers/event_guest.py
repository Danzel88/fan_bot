from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.emoji import emojize
from database import database as db
from dialogs import msg


presence = ["Оставить отзыв", "Подписаться на новости"]
person_role = ["Гость", "Спикер", "Организатор"]
age_interval = ["16-20", "21-25", "26-30", "31-35", "36-40", "40-50", "50+"]
city = ["Москва", "Другой"]

photo_dir = "photos/"


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
    user_data = await db.select_user(message.from_user.id)
    if user_data is not None:
        if message.from_user.id == user_data[-1] and user_data[-2] is None:
            await message.answer(f'Ты уже зарегался в боте. Что бы оставить отзыв '
                                 f'подтверди посещение кнопкой или подпишись на новости',
                                 reply_markup=keyboard)
            return
        elif user_data[1] == presence[1]:
            accept_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            accept_kb.add(presence[0])
            await message.answer(f'Ты уже подписан на новости. Что бы оставить отзыв, подиверди посещение кнопкой',
                                 reply_markup=accept_kb)
            return
        elif user_data[-2] is None:
            await message.answer(f'Сброшено состояние посещения')
            await db.create_or_update_user(tg_id=message.from_user.id)
            return
        else:
            await message.answer(f'Ты уже оставлял отзыв. Спасибо',
                                 reply_markup=types.ReplyKeyboardRemove())
            return
    await message.answer(f"{msg.grete}😉", reply_markup=keyboard)
    await FaneronUsers.init_state.set()
    await db.create_user(tg_id=int(message.from_user.id))


# async def delayed_registration(message: types.Message, state: FSMContext):
#     await state.update_data(presence=presence[0])
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     for role in person_role:
#         keyboard.add(role)
#     await FaneronUsers.next()
#     await message.answer(f"Круто! Мы тебя ждали! В качестве кого был на мероприятии?", reply_markup=keyboard)
#     await db.update_user(presence=presence[0], tg_id=message.from_user.id)


async def pres_accept(message: types.Message, state: FSMContext):
    if message.text not in presence:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(presence=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for role in person_role:
        keyboard.add(role)
    if message.text == presence[1]:
        accept_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        accept_kb.add(presence[0])
        await db.create_or_update_user(presence=message.text.lower(), tg_id=message.from_user.id)
        await message.answer(
            f'Ты будешь получать новости до конца мероприятия. Что бы оставить отзыв подтверди посещение кнопкой',
            reply_markup=accept_kb)
        return
    await FaneronUsers.next()
    await db.create_or_update_user(presence=message.text.lower(), tg_id=message.from_user.id)
    await message.answer(f"{msg.change_role}", reply_markup=keyboard)


async def role_chosen(message: types.Message, state: FSMContext):
    if message.text not in person_role:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(role=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for age in age_interval:
        keyboard.add(age)
    await FaneronUsers.next()
    await message.answer(f"{msg.change_age_interval}", reply_markup=keyboard)


async def age_chosen(message: types.Message, state: FSMContext):
    if message.text not in age_interval:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(age=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in city:
        keyboard.add(c)
    await FaneronUsers.next()
    await message.answer(f"{msg.change_city}", reply_markup=keyboard)


async def city_chosen(message: types.Message, state: FSMContext):
    if message.text not in city:
        await message.answer(f'Выбери из предложенных вариантов')
        return
    await state.update_data(city=message.text.lower())
    await FaneronUsers.next()
    await message.answer(f'{msg.get_review_and_message}',
                         reply_markup=types.ReplyKeyboardRemove())


async def get_review(message: types.Message, state: FSMContext):
    await state.update_data(review=message.text)
    await state.update_data(tg_id=message.from_user.id)
    user_data = await state.get_data()
    # await message.photo[-1].download(
    #     destination_file=f'{photo_dir}{message.from_user.id}.jpg')
    await message.answer(f"{msg.final_msg}")
    await state.finish()
    await db.update_user(presence=user_data["presence"], person_role=user_data['role'],
                         age=user_data["age"], city=user_data["city"],
                         review=str(user_data["review"]), tg_id=user_data["tg_id"])


def register_faneron_users_handler(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(init_user, commands='start', state='*')
    dp.register_message_handler(pres_accept, state=FaneronUsers.init_state)
    dp.register_message_handler(role_chosen, state=FaneronUsers.waiting_for_presence_accept)
    dp.register_message_handler(age_chosen, state=FaneronUsers.waiting_for_role)
    dp.register_message_handler(city_chosen, state=FaneronUsers.waiting_for_age)
    dp.register_message_handler(get_review, state=FaneronUsers.waiting_for_city)  # Lj,fdbnm content_types=['photo']
    # dp.register_message_handler(delayed_registration, commands='check_in', state=FaneronUsers.init_state)
