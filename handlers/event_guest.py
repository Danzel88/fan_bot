from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import keyboard
from database import database as db
from dialogs import msg, services
from keyboard import greet_markup, managers, managers_rating, common_rating


class SurAgencyClient(StatesGroup):
    waiting_for_init_client = State()
    waiting_for_general_info = State()
    waiting_for_manager_name = State()
    waiting_for_manager_rating = State()
    waiting_return_probability = State()
    waiting_common_rating = State()
    waiting_rating_manager = State()
    waiting_review_us = State()
    waiting_repeat_chance = State()


async def init_client(message: types.Message):
    await message.answer(msg.greete)
    await sleep(1)
    await message.answer(msg.greete_continues, reply_markup=greet_markup)
    await SurAgencyClient.waiting_for_init_client.set()


async def process_general_information(message: types.Message, state: FSMContext):
    await state.update_data(client_state=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.general_information, reply_markup=ReplyKeyboardRemove())


async def process_manager_name(message: types.Message, state: FSMContext):
    await state.update_data(general_information=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.manager_name, reply_markup=managers)


async def process_managers_rating(message: types.Message, state: FSMContext):
    await state.update_data(manager_name=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.rating_manager, reply_markup=managers_rating)


async def process_review_text(message: types.Message, state: FSMContext):
    await state.update_data(managers_rating=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.review_us, reply_markup=ReplyKeyboardRemove())


async def process_return_probability(message: types.Message, state: FSMContext):
    await state.update_data(review_text=message.text)
    await SurAgencyClient.next()
    await message.answer(msg.repeat_chance, reply_markup=common_rating)


async def process_common_rating(message: types.Message, state: FSMContext):
    await state.update_data(return_probability=message.text)
    await SurAgencyClient.next()
    pres = open('sender_data/SUR Agency.pdf', 'rb')
    if message.text == keyboard.you_cool:
        await message.answer(msg.you_cool_answer, reply_markup=ReplyKeyboardRemove())
        await message.reply_document(pres)


def register_sur_client_handler(dp: Dispatcher):
    dp.register_message_handler(init_client, commands='start', state='*')
    dp.register_message_handler(process_general_information, state=SurAgencyClient.waiting_for_init_client)
    dp.register_message_handler(process_manager_name, state=SurAgencyClient.waiting_for_general_info)
    dp.register_message_handler(process_managers_rating, state=SurAgencyClient.waiting_for_manager_name)
    dp.register_message_handler(process_review_text, state=SurAgencyClient.waiting_for_manager_rating)
    dp.register_message_handler(process_return_probability, state=SurAgencyClient.waiting_return_probability)
    dp.register_message_handler(process_common_rating, state=SurAgencyClient.waiting_common_rating)
