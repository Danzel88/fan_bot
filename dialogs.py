from dataclasses import dataclass


@dataclass(frozen=True)
class Messages:
    grete: str = 'Привет. Я бот Фанерона. Если ты уже посетил событие, то ' \
                 'жми «Оставить отзыв» и делись впечатлениями 😉'
    attention_about_review: str = '❗️Важно. Оставить отзыв можно только один раз'
    promo_code: str = "⚡️ Кстати, всем новым пользователям мы даем секретный промокод. " \
                      "Вводи F50 при оформлении билета " \
                      "на сайте и получи 50% скидку."
    change_event_place: str = "Расскажи, где ты был?"
    change_age_interval: str = "Сколько тебе лет?"
    change_city: str = "Напиши, из какого ты города?"
    get_review_and_message: str = "Напиши, что тебя больше всего впечатлило?" \

    final_msg: str = "Спасибо за отзыв и за то, что побывал в нашей метавселенной. " \
                     "Присоединяйся к Фанерону в " \
                     "<a href='https://vk.com/faneron_space'>соцсетях</a> " \
                     " или следи за событиями " \
                     "на <a href='https://faneron.ru'>сайте</a> 🙌"
    subscribe_answer: str = "Теперь тебе будут приходить все самые важные новости из Города мечты."
    review_already_exists: str = "Я уже получил твой отзыв. Но буду рад, если ты останешься 👍"
    registration_done: str = "Твоя регистрация в боте ✅ Теперь можешь оставить отзыв или подписаться на новости"
    already_subscribe: str = "У тебя уже есть подписка на новости"
    change_on_exists_variable = "Выбери из предложенных вариантов"
    wrong_format_age: str = "Введи возраст цифрами"
    spam_handler: str = "Если хочешь пообщаться, то заходи в <a href='https://instagram.com/faneron.ru'>Инстаграм</a> " \
                        "Фанерона. Там игры, опросы, розыгрыши и классное комьюнити"
    spam_handler_tmp = ""
    trouble_shutting: str = "❔У тебя появились проблемы с отзывом? Просто отправь команду /start"
    message_for_sender: str = "Это функция рассылки. Сообщения будут отправлены всем пользователям бота." \
                              " Пришли сообщение, которое нужно разослать.\n" \
                              "<b>НЕ ЗАБУДЬ ПРОВЕРИТЬ ТЕСТОВОЙ РАССЫЛКОЙ!!!</b>\n/test_sender"
    message_for_test_sender: str = "Тестовая отправка сообщения перед рассылкой всем пользователям!\n" \
                                   "<b>НЕ ЗАБУДЬ ОТПРАВИТЬ ВСЕМ</b>🍑"
    photo_limit: str = "Вижу в тебе задатки хорошего блогера, поделись всеми своими фотографиями в соцсетях," \
                       " а мне достаточно и тех, что я уже получил"
    first_step_reply_start_command: str = "Я бот Фанерона. Если ты уже посетил событие, " \
                                         "то жми «Оставить отзыв» и делись впечатлениями 😉"


reply_start = ["Уже стартовали, не дави на меня!", "Стартуем!!!",
               "Ответь пожалуйста на полседнее сообщение",
               "Позволь я повторю последний вопрос?",
               "Может закончим с опросом, потом обсудим что хочешь?"]

msg = Messages()

