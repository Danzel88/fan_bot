import asyncio
import datetime
import json
import logging

from aiogram import types
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import exceptions

from bot import bot, config
from database import mailing_database
from dialogs import msg


formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'

logging.basicConfig(
    filename=f'/log/bot-from-{datetime.datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)


class Sender(StatesGroup):
    waiting_init_admin = State()
    waiting_message_from_admin = State()
    waiting_message_from_admin_to_test_mailing = State()
    waiting_message_id = State()


async def init_sender_state(message: types.Message):
    """инициализация рассылки"""
    if message.text == "/test_sender":
        await message.answer(f'{msg.message_for_test_sender}', parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
        await Sender.waiting_message_from_admin_to_test_mailing.set()
        return
    await message.answer(f'{msg.message_for_sender}', parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    await Sender.waiting_message_from_admin.set()


async def send_message(message: types.Message,
                       user_id: int, disable_notification: bool = False) -> bool:
    """Отправка сообщений"""
    try:
        if message.text is not None:
            await bot.send_message(chat_id=user_id, text=message.text,
                                   disable_notification=disable_notification,
                                   parse_mode="HTML")
        elif message.photo is not None:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption,
                                 disable_notification=disable_notification, parse_mode="HTML")
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id=user_id, message=message)
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.warning(f"Target [ID:{user_id}]: failed")
    else:
        logging.warning(f"Target [ID:{user_id}]: success.")
        return True
    return False


async def test_sender(message: types.Message, state: FSMContext):
    """тестовая рассылка. Сообщение придет только админу"""
    logging.warning(f'Запуск тестовой рассылки')
    sent_message = {}
    try:
        await send_message(user_id=config.tg_bot.admin_id, message=message)
        sent_message[message.from_user.id] = message.message_id + 1
    except IndexError:
        logging.error(f'нет пользователей для отправки')
    finally:
        await message.answer(f'Номер рассылки для удаления {int(message.message_id) + 1}')
        await state.finish()
        with open(f"sender_data/{message.message_id + 1}.json", 'w') as f:
            json.dump(sent_message, f)


async def start_spam(message: types.Message, state: FSMContext):
    """Запуск рассылки. Получаем всех пользователей из БД. Шарашим по айдишникам из спика и в дикт пишем пару
    tg_id: message_id, (дампим в json с именем message_id первого отпавленного сообщения, админ получит
    ответом этот номер) что бы иметь возможность удалить потом рассылку (для этого нужно указывать id чата,
    он же tg_id и message_id) message_id инкерентируюем +1 с каждым следующим отправленным сообщением"""
    logging.warning(f'Запущена рассылка')
    all_users = await mailing_database.get_all_users()
    users_list = tuple(zip(*all_users))
    count = 0
    sent_message = {}
    try:
        for user_id in users_list[0]:
            if await send_message(user_id=user_id, message=message):
                sent_message[user_id] = message.message_id + 1 + count
                count += 1
            await asyncio.sleep(.05)
    except IndexError:
        logging.error(f'нет пользователей для отправки')
    finally:
        await message.answer(f'Номер рассылки для удаления {int(message.message_id) + 1}')
        await state.finish()
        logging.warning(f'{count} сообщений отправлено')
        with open(f"sender_data/{message.message_id + 1}.json", 'w') as f:
            json.dump(sent_message, f)


async def del_init(message: types.Message):
    """инициализация удаления рассылки"""
    await message.answer(f'Пришли номер рассылки которую нужно удалить')
    await Sender.waiting_message_id.set()
    logging.warning(f'Пользователем {message.from_user.id} запущено удаление рассылки')


async def delete_send_message(message: types.Message, state: FSMContext):
    """Метод получем номер рассылки, по этому имени получет json файл и из каждого чата удаяет сообщение с
    соответсвующим id. Как формируется это файл описано в start_spam"""
    try:
        with open(f'sender_data/{message.text}.json') as f:
            data = json.load(f)
        for k in data:
            await bot.delete_message(chat_id=k, message_id=data[k])
        await asyncio.sleep(0.5)
        await state.finish()
        logging.warning(f'Рассылка {message.text} удалена')
    except FileNotFoundError:
        logging.warning(f'Mailing number {message.text} not found')
        await message.answer("Нет рассылки с таким номером")

def register_sender(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(init_sender_state, IDFilter(user_id=admin_id), commands="sender", state="*")
    dp.register_message_handler(init_sender_state, IDFilter(user_id=admin_id), commands="test_sender", state="*")
    dp.register_message_handler(del_init, IDFilter(user_id=admin_id), commands="del_send", state="*")
    dp.register_message_handler(delete_send_message, state=Sender.waiting_message_id)
    dp.register_message_handler(start_spam, IDFilter(user_id=admin_id), state=Sender.waiting_message_from_admin,
                                content_types=['text', 'photo'])
    dp.register_message_handler(test_sender, IDFilter(user_id=admin_id),
                                state=Sender.waiting_message_from_admin_to_test_mailing,
                                content_types=['text', 'photo'])
