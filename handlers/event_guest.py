import asyncio
import logging
import os
import datetime
import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import database as db
from dialogs import msg, services
from keyboard import inline_kb, inline_accept_kb


# presence = ["Оставить отзыв", "Подписаться на новости"]
# person_role = ["Гость", "Спикер", "Организатор"]
# formatter = '[%(asctime)s] %(levelname)8s --- %(message)s ' \
#             '(%(filename)s:%(lineno)s)'
# logging.basicConfig(
#     filename=f'log/bot-from-'
#              f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
#     filemode='w',
#     format=formatter,
#     datefmt='%Y-%m-%d %H:%M:%S',
#     level=logging.WARNING)


class SurAgencyClient(StatesGroup):
    waiting_for_company_name = State()
    waiting_for_position = State()
    waiting_for_name = State()
    waiting_for_done_project = State()
    waiting_service_list = State()
    waiting_manager_name = State()
    waiting_rating_manager = State()
    waiting_review_us = State()
    waiting_repeat_chance = State()


async def init_user(message: types.Message):
    await message.answer(msg.company_name)
    await SurAgencyClient.waiting_for_company_name.set()


async def process_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.position)


async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.name)


async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.done_project)


async def process_done_project(message: types.Message, state: FSMContext):
    await state.update_data(done_project=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.service_list, reply_markup=inline_kb)
    await message.answer("После выбора услуг нужно подтвердить ", reply_markup=inline_accept_kb)


async def process_service_list(state: FSMContext, data: list):
    # await SurAgencyClient.next()
    await state.update_data(service_list=data)


async def callback_handler(callback: types.CallbackQuery, state: FSMContext):
    #TODO ДОписать appen к списку услуг
    await callback.answer("Запомнил")
    service_list = []
    await process_service_list(state, service_list)


async def accept_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    #TODO дописать nextstate
    await callback.answer(" ")
    data = await state.get_data()
    print(data['company_name'], data['position'], data['name'],
          data['done_project'], data['service_list'])
    await SurAgencyClient.next()

# async def process_presence(message: types.Message, state: FSMContext):
#     """Получаем от юзера его статус (Подписка на новости или Оставить отзыв)"""
#     if message.text not in presence:
#         await message.answer(f'{msg.change_on_exists_variable}')
#         return
#     await state.update_data(presence=message.text)
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     for role in person_role:
#         keyboard.add(role)
#     if message.text == presence[1]:
#         accept_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         accept_kb.add(presence[0])
#         await db.create_or_update_user(presence=message.text, tg_id=message.from_user.id)
#         await message.answer(
#             f'{msg.subscribe_answer}',
#             reply_markup=accept_kb)
#         return
#     await FaneronUsers.next()
#     await db.create_or_update_user(presence=message.text, tg_id=message.from_user.id)
#     await message.answer(f"{msg.change_role}", reply_markup=keyboard)
#
#
# async def process_role(message: types.Message, state: FSMContext):
#     """Получеам от пользователя его роль на мероприятии"""
#     if message.text not in person_role:
#         await message.answer(f'{msg.change_on_exists_variable}')
#         return
#     await state.update_data(role=message.text)
#     await FaneronUsers.next()
#     await message.answer(f"{msg.change_age_interval}", reply_markup=types.ReplyKeyboardRemove())
#
#
# async def process_age(message: types.Message, state: FSMContext):
#     """Получем возраст"""
#     if message.text.isdigit():
#         if int(message.text) > 118:
#             await message.answer(f"Ты супер стар. Напиши реальный возраст, это важно!")
#             return
#         await state.update_data(age=message.text)
#         await FaneronUsers.next()
#         await message.answer(f"{msg.change_city}", reply_markup=types.ReplyKeyboardRemove())
#     else:
#
#         await message.answer(f"{msg.wrong_format_age}")
#
#
# async def process_city(message: types.Message, state: FSMContext):
#     """Получеам город"""
#     await state.update_data(city=message.text)
#     await FaneronUsers.next()
#     await message.answer(f'{msg.get_review_and_message}',
#                          reply_markup=types.ReplyKeyboardRemove())
#
#
# async def write_db_user_data(state: FSMContext):
#     """Пишем в БД полученные данные (статус, роль, возраст, город, ревью)"""
#     user_data = await state.get_data()
#     await db.update_user(presence=user_data['presence'], person_role=user_data["role"],
#                          age=user_data["age"], city=user_data["city"],
#                          review=user_data["review"], tg_id=user_data["tg_id"])
#
#
# async def process_review(message: types.Message, state: FSMContext):
#     """Получем текст отзыва и фотографии. В Зависимости от контекста сообщения запускаем обработку медиа из сообщения"""
#     if message.photo:
#         if not message.caption:
#             await asyncio.sleep(1.0)
#             await process_photo(message, state)
#             return
#         else:
#             await asyncio.sleep(1.0)
#             await process_photo(message, state)
#             await state.update_data(review=message.caption)
#             await state.update_data(tg_id=message.from_user.id)
#             await write_db_user_data(state)
#     else:
#         await state.update_data(review=message.text)
#         await state.update_data(tg_id=message.from_user.id)
#         await write_db_user_data(state)
#     await message.answer(f"{msg.final_msg}")
#     await FaneronUsers.next()
#
#
# async def process_photo(message: types.Message, state: FSMContext):
#     """Обработчик фотографий. Сохраняем фото с уникальным именем. Огарничение 30 фото от одного пользователя"""
#     photo_dir = f"{os.getcwd()}/photos"
#     photo_name = f"{message.from_user.id}"
#     await message.photo[-1].download(destination_file=f"{photo_dir}/{photo_name}/{photo_name}_{datetime.datetime.now().time()}.jpg")
#     if len(os.listdir(f"{photo_dir}/{photo_name}")) >= 30:
#         await message.answer(f"{msg.photo_limit}")
#         await state.finish()
#         return
#     logging.warning(f"user {message.from_user.id} add photo")
#
#
# async def spam_process(message: types.Message, state: FSMContext):
#     """Обработка сообщений отправленных после отзыва и фото... или до отзыва... или где то в середине, короче отлов
#     спама"""
#     await message.answer(f'{msg.spam_handler}', parse_mode="HTML")
#     await asyncio.sleep(1.0)
#     await message.answer(f'{msg.trouble_shutting}', parse_mode="HTML")


def register_faneron_users_handler(dp: Dispatcher):
    dp.register_message_handler(init_user, commands='start', state='*')
    dp.register_message_handler(process_company_name, state=SurAgencyClient.waiting_for_company_name)
    dp.register_message_handler(process_position, state=SurAgencyClient.waiting_for_position)
    dp.register_message_handler(process_name, state=SurAgencyClient.waiting_for_name)
    dp.register_message_handler(process_done_project, state=SurAgencyClient.waiting_for_done_project)
    # dp.register_message_handler(process_service_list, state=SurAgencyClient.waiting_service_list)
    dp.register_callback_query_handler(callback_handler,
                                       Text(startswith=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']),
                                       state=SurAgencyClient.waiting_service_list)
    dp.register_callback_query_handler(accept_callback_handler, text='ppp',
                                       state=SurAgencyClient.waiting_service_list)

    # dp.register_message_handler(process_photo, state=FaneronUsers.waiting_manager_name,
    #                             content_types=['photo'])
    # dp.register_message_handler(spam_process, state="*")
