import asyncio
import logging
import os
import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import database as db
from dialogs import msg


presence = ["Оставить отзыв", "Подписаться на новости"]
person_role = ["Гость", "Спикер", "Организатор"]
formatter = '[%(asctime)s] %(levelname)8s --- %(message)s ' \
            '(%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'log/bot-from-'
             f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING)


class FaneronUsers(StatesGroup):
    waiting_for_presence_accept = State()
    waiting_for_role = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_review = State()
    waiting_photo = State()


async def init_user(message: types.Message):
    """Инициализация пользователя в БД. Создаем в запусь с tg_id.
    В условиях проверяем есть ли пользователь в БД. Если есть проверяем оставлял ли он уже отзыв.
    Все эти проверки нужны для того, что бы в случае перезапуска бота, юзер был где то на промежуточном стэйте,
    можно было ему сказать о необходимости перезапустить свою инициализацию

    Отправляем приветственные сообщения"""
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
    await message.answer(f"{msg.grete}")
    await asyncio.sleep(1.0)
    await message.answer(f"{msg.attention_about_review}")
    await asyncio.sleep(1.0)
    await message.answer(f"{msg.promo_code}", reply_markup=keyboard)
    await FaneronUsers.waiting_for_presence_accept.set()
    await db.create_user(tg_id=int(message.from_user.id))


async def process_presence(message: types.Message, state: FSMContext):
    """Получаем от юзера его статус (Подписка на новости или Оставить отзыв)"""
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
    """Получеам от пользователя его роль на мероприятии"""
    if message.text not in person_role:
        await message.answer(f'{msg.change_on_exists_variable}')
        return
    await state.update_data(role=message.text)
    await FaneronUsers.next()
    await message.answer(f"{msg.change_age_interval}", reply_markup=types.ReplyKeyboardRemove())


async def process_age(message: types.Message, state: FSMContext):
    """Получем возраст"""
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
    """Получеам город"""
    await state.update_data(city=message.text)
    await FaneronUsers.next()
    await message.answer(f'{msg.get_review_and_message}',
                         reply_markup=types.ReplyKeyboardRemove())


async def write_db_user_data(state: FSMContext):
    """Пишем в БД полученные данные (статус, роль, возраст, город, ревью)"""
    user_data = await state.get_data()
    await db.update_user(presence=user_data['presence'], person_role=user_data["role"],
                         age=user_data["age"], city=user_data["city"],
                         review=user_data["review"], tg_id=user_data["tg_id"])


async def process_review(message: types.Message, state: FSMContext):
    """Получем текст отзыва и фотографии. В Зависимости от контекста сообщения запускаем обработку медиа из сообщения"""
    if message.photo:
        if not message.caption:
            await asyncio.sleep(1.0)
            await process_photo(message, state)
            return
        else:
            await asyncio.sleep(1.0)
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
    """Обработчик фотографий. Сохраняем фото с уникальным именем. Огарничение 30 фото от одного пользователя"""
    photo_dir = f"{os.getcwd()}/photos"
    photo_name = f"{message.from_user.id}"
    await message.photo[-1].download(destination_file=f"{photo_dir}/{photo_name}/{photo_name}_{datetime.datetime.now().time()}.jpg")
    if len(os.listdir(f"{photo_dir}/{photo_name}")) >= 30:
        await message.answer(f"{msg.photo_limit}")
        await state.finish()
        return
    logging.warning(f"user {message.from_user.id} add photo")


async def spam_process(message: types.Message, state: FSMContext):
    """Обработка сообщений отправленных после отзыва и фото... или до отзыва... или где то в середине, короче отлов
    спама"""
    await message.answer(f'{msg.spam_handler}', parse_mode="HTML")
    await asyncio.sleep(1.0)
    await message.answer(f'{msg.trouble_shutting}', parse_mode="HTML")


def register_faneron_users_handler(dp: Dispatcher):
    dp.register_message_handler(init_user, commands='start', state='*')
    dp.register_message_handler(process_presence, state=FaneronUsers.waiting_for_presence_accept)
    dp.register_message_handler(process_role, state=FaneronUsers.waiting_for_role)
    dp.register_message_handler(process_age, state=FaneronUsers.waiting_for_age)
    dp.register_message_handler(process_city, state=FaneronUsers.waiting_for_city)
    dp.register_message_handler(process_review, state=FaneronUsers.waiting_review, content_types=['photo', 'text'])
    dp.register_message_handler(process_photo, state=FaneronUsers.waiting_photo, content_types=['photo'])
    dp.register_message_handler(spam_process, state="*")
