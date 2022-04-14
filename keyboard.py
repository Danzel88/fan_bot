from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# inline_a = InlineKeyboardButton('Таргетированная реклама', callback_data='a')
# inline_b = InlineKeyboardButton('Медийная, контекстная или programmatic реклама', callback_data='b')
# inline_c = InlineKeyboardButton('Работа со СМИ', callback_data='c')
# inline_d = InlineKeyboardButton('Наружная реклама', callback_data='d')
# inline_e = InlineKeyboardButton('Работа с инфлюенсерами', callback_data='e')
# inline_f = InlineKeyboardButton('Услуги по созданию сайта', callback_data='f')
# inline_g = InlineKeyboardButton('Услуги дизайна', callback_data='g')
# inline_h = InlineKeyboardButton('E-mail рассылки', callback_data='h')
# inline_i = InlineKeyboardButton('SMM', callback_data='i')
# inline_j = InlineKeyboardButton('Фото и видеосъемка', callback_data='j')
# inline_accept = InlineKeyboardButton('ГОТОВО', callback_data='ppp')
# inline_kb = InlineKeyboardMarkup(row_width=1).add(inline_a, inline_b, inline_c, inline_b, inline_e, inline_f, inline_g,
#                                        inline_h, inline_i, inline_j)
# inline_accept_kb = InlineKeyboardMarkup(row_width=1).add(inline_accept)



soulful_bot = KeyboardButton("И тебе привет, бот с душой")
angry_client = KeyboardButton("Мне срочно нужно выговориться")
greet_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(soulful_bot).add(angry_client)
