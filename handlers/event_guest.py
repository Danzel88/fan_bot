import asyncio
from asyncio import sleep
from random import choice

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import database as db
from dialogs import msg, reply_start


presence = ["Оставить отзыв"]
event_place = ["Экспозиция", "Лаборатория", "Оба пространства"]


class FaneronUsers(StatesGroup):
    waiting_for_presence_accept = State()
    waiting_for_event_place = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_review = State()
    waiting_photo = State()


async def init_user(message: types.Message, state: FSMContext):
    """Инициализация пользователя в БД. Создаем в запусь с tg_id.
    В условиях проверяем есть ли пользователь в БД. Если есть проверяем оставлял ли он уже отзыв.
    Все эти проверки нужны для того, что бы в случае перезапуска бота, юзер был где то на промежуточном стэйте,
    можно было ему сказать о необходимости перезапустить свою инициализацию

    Отправляем приветственные сообщения"""
    accept_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    accept_kb.add(presence[0])
    user_state = await state.get_state()
    try:
        user_data = await db.select_user(message.from_user.id)
        int(user_data[0])
        await message.answer(f'{msg.review_already_exists}',
                             reply_markup=types.ReplyKeyboardRemove())
    except TypeError:
        if user_state is None:
            await message.answer(f"{msg.grete}")
            await asyncio.sleep(0.5)
            await message.answer(f"{msg.attention_about_review}", reply_markup=accept_kb)
            await FaneronUsers.waiting_for_presence_accept.set()
            await state.update_data(last_message=msg.first_step_reply_start_command)
        elif user_state is not None:
            await message.answer(choice(reply_start))
            last_msg = await state.get_data()
            await sleep(0.5)
            await message.answer(last_msg["last_message"])


async def process_presence(message: types.Message, state: FSMContext):
    """Получаем от юзера его статус (Подписка на новости или Оставить отзыв)"""
    if message.text not in presence:
        await message.answer(f'{msg.change_on_exists_variable}')
        return
    await state.update_data(presence=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for place in event_place:
        keyboard.add(place)
    await FaneronUsers.next()
    await message.answer(f"{msg.change_event_place}", reply_markup=keyboard)
    await state.update_data(last_message=msg.change_event_place)


async def process_event_place(message: types.Message, state: FSMContext):
    """Получеам от пользователя его роль на мероприятии"""
    if message.text not in event_place:
        await message.answer(f'{msg.change_on_exists_variable}')
        return
    await state.update_data(event_place=message.text)
    await FaneronUsers.next()
    await message.answer(f"{msg.change_age_interval}", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(last_message=msg.change_age_interval)


async def process_age(message: types.Message, state: FSMContext):
    """Получем возраст"""
    if message.text.isdigit():
        if int(message.text) > 118:
            await message.answer(f"Ты супер стар. Напиши реальный возраст, это важно!")
            return
        await state.update_data(age=message.text)
        await FaneronUsers.next()
        await message.answer(f"{msg.change_city}", reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(last_message=msg.change_city)
    else:

        await message.answer(f"{msg.wrong_format_age}")


async def process_city(message: types.Message, state: FSMContext):
    """Получеам город"""
    await state.update_data(city=message.text)
    await FaneronUsers.next()
    await message.answer(f'{msg.get_review_and_message}',
                         reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(last_message=msg.get_review_and_message)


async def write_db_user_data(state: FSMContext):
    """Пишем в БД полученные данные (статус, роль, возраст, город, ревью, id_телеги)"""
    user_data = await state.get_data()
    await db.writer(user_data)


async def process_review(message: types.Message, state: FSMContext):
    """Получем текст отзыва и фотографии. В Зависимости от контекста сообщения запускаем обработку медиа из сообщения"""
    if message.photo:
        if not message.caption:
            await asyncio.sleep(1.0)
            return
        else:
            await asyncio.sleep(1.0)
            await state.update_data(review=message.caption)
            await state.update_data(tg_id=message.from_user.id)
            await write_db_user_data(state)
    else:
        await state.update_data(review=message.text)
        await state.update_data(tg_id=message.from_user.id)
        await write_db_user_data(state)
    await message.answer(f"{msg.final_msg}", disable_web_page_preview=True,
                         parse_mode='HTML')
    await state.finish()


async def spam_process(message: types.Message):
    """Обработка сообщений отправленных после отзыва и фото... или до отзыва... или где то в середине, короче отлов
    спама"""
    await message.answer(f'{msg.review_already_exists}', parse_mode="HTML")


def register_faneron_users_handler(dp: Dispatcher):
    dp.register_message_handler(init_user, commands='start', state='*')
    dp.register_message_handler(process_presence, state=FaneronUsers.waiting_for_presence_accept)
    dp.register_message_handler(process_event_place, state=FaneronUsers.waiting_for_event_place)
    dp.register_message_handler(process_age, state=FaneronUsers.waiting_for_age)
    dp.register_message_handler(process_city, state=FaneronUsers.waiting_for_city)
    dp.register_message_handler(process_review, state=FaneronUsers.waiting_review, content_types=['photo', 'text'])
    dp.register_message_handler(spam_process, state="*")
