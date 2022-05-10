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

#greet
soulful_bot = KeyboardButton("И тебе привет, бот с душой")
angry_client = KeyboardButton("Мне срочно нужно выговориться")
#managers names
managers_list = ["Ольга", "Мария", "Карина", "Алина"]
Olga = KeyboardButton(managers_list[0])
Mariya = KeyboardButton(managers_list[1])
Karina = KeyboardButton(managers_list[2])
ALina = KeyboardButton(managers_list[3])
#managers_rating
managers_rating_list = ["🔥 Огненно и зажигательно", "👌 В целом все нормально",
                        "🗿 Ну такое. Я лучше опишу", "😔 Р — разочарование"]
fire = KeyboardButton(managers_rating_list[0])
ok = KeyboardButton(managers_rating_list[1])
so_so = KeyboardButton(managers_rating_list[2])
badly = KeyboardButton(managers_rating_list[3])
#comon_rating
you_cool = "Конечно! Вы шикарны в работе и общении"
middling = "Я подумаю. А что еще вы умеете?"
shit = "Точно нет! Оставлю отзыв и пойду к психологу"

greet_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(soulful_bot).add(angry_client)
managers = ReplyKeyboardMarkup(resize_keyboard=True).add(Olga, Mariya).add(Karina, ALina)
managers_rating = ReplyKeyboardMarkup(resize_keyboard=True).add(fire).add(ok).add(so_so).add(badly)
common_rating = ReplyKeyboardMarkup(resize_keyboard=True).add(you_cool).add(middling).add(shit)

