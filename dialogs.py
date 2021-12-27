from dataclasses import dataclass


@dataclass(frozen=True)
class Messages:
    grete: str = 'Привет. Я бот города Фанерона. Если ты только собираешься в Город мечты, то подписывайся на новости и будь в курсе всего, что происходит. Если ты уже посетил событие, то жми "Оставить отзыв" и делись впечатлениями 😉'
    change_role: str = "Расскажи, в качестве кого ты был на мероприятии?"
    change_age_interval: str = "Сколько тебе лет?" # Ручной ввод названия возраста
    change_city: str = "Напиши из какого ты города?" # Ручной ввод названия города. Возможно с проверкой по списку городов России
    get_review_and_message: str = "Напиши, что тебе понравилось или нет. Можешь прикрепить фотографии (до 2 шт.)."
    final_msg: str = "Спасибо за отзыв. Оставайся в боте, если хочешь знать всё о вселенной Фанерон и ее новостях"
    subscribe_answer: str = "Теперь тебе будут приходить все самые важные новости из Города мечты. А еще секретные промокоды ✨"
    review_already_exists: str = "Я уже получил твой отзыв. Но буду рад, если ты останешься 👍"
    registration_done: str = "Твоя регистрация в боте ✅ Теперь можешь оставить отзыв или подписаться на новости"
    already_subscribe: str = "У тебя уже подписка на новости"
    change_on_exists_variable = "Выбери из предложенных варинатов"

msg = Messages()

