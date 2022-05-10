
from asyncio import sleep
from random import choice

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import keyboard
from database import database as db
from bot import dp as dp_send
from dialogs import msg, cli_answers, not_in_keyboard_answers, reply_start
from keyboard import greet_markup, managers, managers_rating, common_rating, managers_list


class SurAgencyClient(StatesGroup):
    init_client = State()
    waiting_for_general_info = State()
    waiting_for_manager_name = State()
    waiting_for_manager_rating = State()
    waiting_return_probability = State()
    waiting_review_us = State()


async def init_client(message: types.Message, state: FSMContext):
    client_state = await state.get_state()
    try:
        user = db.select_user(message.from_user.id)
        int(user[0])
        await message.answer(msg.surf_mind, parse_mode='HTML')
    except TypeError:
        if client_state is None:
            await message.answer(msg.greete)
            await sleep(1)
            await message.answer(msg.greete_continues, reply_markup=greet_markup)
            await SurAgencyClient.init_client.set()
            await state.update_data(last_msg=msg.greete_continues)
        elif client_state is not None:
            await message.answer(choice(reply_start))
            last_msg = await state.get_data()
            await message.answer(last_msg["last_msg"])


async def greeting_process(message: types.Message, state: FSMContext):
    if message.text == cli_answers.init_pos or message.text == cli_answers.init_neg:
        await state.update_data(client_state=message.text)
        await message.answer(msg.general_information, reply_markup=ReplyKeyboardRemove())
        await state.update_data(last_msg=msg.general_information)
        await SurAgencyClient.next()
    else:
        await message.answer(choice(not_in_keyboard_answers))


async def get_name_position_project(message: types.Message, state: FSMContext):
    await state.update_data(client_info=message.text)
    await message.answer(msg.manager_name, reply_markup=managers)
    await state.update_data(last_msg=msg.manager_name)
    await SurAgencyClient.next()


async def process_manager_name(message: types.Message, state: FSMContext):
    if message.text in managers_list:
        await state.update_data(manager_name=message.text)
        await SurAgencyClient.next()
        await message.answer(msg.rating_manager, reply_markup=managers_rating)
        await state.update_data(last_msg=msg.rating_manager)
    else:
        await message.answer(choice(not_in_keyboard_answers))


async def process_managers_rating(message: types.Message, state: FSMContext):
    if message.text in keyboard.managers_rating_list:
        await state.update_data(managers_rating=message.text)
        await SurAgencyClient.next()
        await message.answer(msg.review_us, reply_markup=ReplyKeyboardRemove())
        await state.update_data(last_msg=msg.review_us)
    else:
        await message.answer(choice(not_in_keyboard_answers))


async def process_review_text(message: types.Message, state: FSMContext):
    await state.update_data(review_text=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.repeat_chance, reply_markup=common_rating)
    await state.update_data(last_msg=msg.repeat_chance)


async def process_common_rating(message: types.Message, state: FSMContext):
    await state.update_data(return_probability=message.text)
    await state.update_data(tg_id=message.from_user.id)
    pres = open('sender_data/SUR_Agency.pdf', 'rb')
    if message.text == keyboard.you_cool:
        await message.answer(msg.you_cool_answer, reply_markup=ReplyKeyboardRemove())
    elif message.text == keyboard.middling:
        await message.answer(msg.middling_answer, reply_markup=ReplyKeyboardRemove())
    elif message.text == keyboard.shit:
        await message.answer(msg.shit_answer, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(choice(not_in_keyboard_answers))
        return None
    await dp_send.bot.send_document(message.from_user.id, pres)
    data = await state.get_data()
    db.writer(data)
    await state.finish()


async def spam_process(message: types.Message, state: FSMContext):
    """Обработка сообщений отправленных после отзыва и фото... или до отзыва... или где то в середине, короче отлов
    спама"""
    await message.answer(msg.surf_mind, parse_mode='HTML')


def register_sur_client_handler(dp: Dispatcher):
    dp.register_message_handler(init_client, commands='start', state='*')
    dp.register_message_handler(greeting_process, state=SurAgencyClient.init_client)
    dp.register_message_handler(get_name_position_project, state=SurAgencyClient.waiting_for_general_info)
    dp.register_message_handler(process_manager_name, state=SurAgencyClient.waiting_for_manager_name)
    dp.register_message_handler(process_managers_rating, state=SurAgencyClient.waiting_for_manager_rating)
    dp.register_message_handler(process_review_text, state=SurAgencyClient.waiting_return_probability)
    dp.register_message_handler(process_common_rating, state=SurAgencyClient.waiting_review_us)
    dp.register_message_handler(spam_process, state="*")