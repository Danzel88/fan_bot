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
    await state.update_data(service_list=[])
    await SurAgencyClient.next()
    await message.answer(msg.service_list, reply_markup=inline_kb)
    await message.answer("После выбора услуг нужно подтвердить ", reply_markup=inline_accept_kb)


async def callback_handler(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        s = services[callback.data]
        if s in data['service_list']:
            await callback.answer("Уже выбрана",show_alert=True)
        else:
            await callback.answer("Запомнил")
            data['service_list'].append(services[callback.data])


async def accept_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(" ")
    await SurAgencyClient.next()
    # data = await state.get_data()
    # print(data['service_list'])
    await callback.message.answer(msg.manager_name)


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
