import asyncio
import os
import time

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import database as db
from dialogs import msg


presence = ["Оставить отзыв", "Подписаться на новости"]
person_role = ["Гость", "Спикер", "Организатор"]
age_interval = ["16-20", "21-25", "26-30", "31-35", "36-40", "40-50", "50+"]
city = ["Москва", "Другой"]


class FaneronUsers(StatesGroup):
    waiting_for_presence_accept = State()
    waiting_for_role = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_review = State()
    waiting_photo = State()


async def init_user(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for pres in presence:
        keyboard.add(pres)
    user_data = await db.select_user(message.from_user.id)
    if user_data is not None:
        if message.from_user.id == user_data[-1] and user_data[-2] is None:
            await message.answer(f'{msg.registration_done}',
                                 reply_markup=keyboard)
            await FaneronUsers.waiting_for_presence_accept.set()
            return
        elif user_data[1] == presence[1]:
            accept_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            accept_kb.add(presence[0])
            await message.answer(f'{msg.already_subscribe}',
                                 reply_markup=accept_kb)
            await FaneronUsers.waiting_for_presence_accept.set()
            return
        elif user_data[1] == presence[0] and user_data[-2] != "None":
            await message.answer(f'{msg.review_already_exists}',
                                 reply_markup=types.ReplyKeyboardRemove())
            return
        elif user_data[1] == presence[0] and user_data[-2] == "None":
            await message.answer(f'{msg.registration_done}',
                                 reply_markup=keyboard)
            await FaneronUsers.waiting_for_presence_accept.set()
            return
        else:
            await message.answer(f'{msg.review_already_exists}',
                                 reply_markup=types.ReplyKeyboardRemove())
            return
    await message.answer(f"{msg.grete}", reply_markup=keyboard)
    await FaneronUsers.waiting_for_presence_accept.set()
    await db.create_user(tg_id=int(message.from_user.id))


async def process_presence(message: types.Message, state: FSMContext):
    if message.text not in presence:
        await message.answer(f'{msg.change_on_exists_variable}')
        return
    await state.update_data(presence=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for role in person_role:
        keyboard.add(role)
    if message.text == presence[1]:
        accept_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        accept_kb.add(presence[0])
        await db.create_or_update_user(presence=message.text, tg_id=message.from_user.id)
        await message.answer(
            f'{msg.subscribe_answer}',
            reply_markup=accept_kb)
        return
    await FaneronUsers.next()
    await db.create_or_update_user(presence=message.text, tg_id=message.from_user.id)
    await message.answer(f"{msg.change_role}", reply_markup=keyboard)


async def process_role(message: types.Message, state: FSMContext):
    if message.text not in person_role:
        await message.answer(f'{msg.change_on_exists_variable}')
        return
    await state.update_data(role=message.text)
    await FaneronUsers.next()
    await message.answer(f"{msg.change_age_interval}", reply_markup=types.ReplyKeyboardRemove())


async def process_age(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) > 118:
            await message.answer(f"Ты супер стар. Напиши реальный возраст, это важно!")
            return
        await state.update_data(age=message.text)
        await FaneronUsers.next()
        await message.answer(f"{msg.change_city}", reply_markup=types.ReplyKeyboardRemove())
    else:

        await message.answer(f"{msg.wrong_format_age}")


async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await FaneronUsers.next()
    await message.answer(f'{msg.get_review_and_message}',
                         reply_markup=types.ReplyKeyboardRemove())


async def write_db_user_data(state: FSMContext):
    user_data = await state.get_data()
    await db.update_user(presence=user_data["presence"], person_role=user_data["role"],
                         age=user_data["age"], city=user_data["city"],
                         review=user_data["review"], tg_id=user_data["tg_id"])


async def process_review(message: types.Message, state: FSMContext):
    if message.photo:
        if not message.caption:
            await asyncio.sleep(1.0)
            await process_photo(message, state)
            return
        else:
            await process_photo(message, state)
            await state.update_data(review=message.caption)
            await state.update_data(tg_id=message.from_user.id)
            await write_db_user_data(state)
    else:
        await state.update_data(review=message.text)
        await state.update_data(tg_id=message.from_user.id)
        await write_db_user_data(state)
    await message.answer(f"{msg.final_msg}")
    await FaneronUsers.next()


async def process_photo(message: types.Message, state: FSMContext):
    print(message)
    photo_dir = f"{os.getcwd()}/photos"
    photo_name = f"{message.from_user.id}"
    tmp = os.getcwd()
    print(tmp)

    if await photo_counter(message.from_user.id):
        await message.photo[-1].download(destination_file=f"{photo_dir}/{photo_name}/{photo_name}-1.jpg")
        # await message.answer(f'Второе фото получили. На этом все. Оставайся с нами')
        await state.finish()
        return
    # await message.answer(f'первое фото получили')
    await message.photo[-1].download(destination_file=f"{photo_dir}/{photo_name}/{photo_name}.jpg")


async def photo_counter(tg_id: int):
    photo_dir = f"{os.getcwd()}/photos"
    photo_name = f"{tg_id}"
    res = os.path.exists(f"{photo_dir}/{photo_name}/{photo_name}.jpg")
    return res


async def spam_process(message: types.Message, state: FSMContext):
    await message.answer(f'Если хочешь пообщаться, то заходи в <a href="https://instagram.com/faneron.ru">Инстаграм</a> Фанерона. Там игры, опросы, розыгрыши и классное комьюнити '
                         f'',
                         parse_mode="HTML")


def register_faneron_users_handler(dp: Dispatcher):
    dp.register_message_handler(init_user, commands='start', state='*')
    dp.register_message_handler(process_presence, state=FaneronUsers.waiting_for_presence_accept)
    dp.register_message_handler(process_role, state=FaneronUsers.waiting_for_role)
    dp.register_message_handler(process_age, state=FaneronUsers.waiting_for_age)
    dp.register_message_handler(process_city, state=FaneronUsers.waiting_for_city)
    dp.register_message_handler(process_review, state=FaneronUsers.waiting_review, content_types=['photo', 'text'])
    dp.register_message_handler(process_photo, state=FaneronUsers.waiting_photo, content_types=['photo'])
    dp.register_message_handler(spam_process, state="*")
