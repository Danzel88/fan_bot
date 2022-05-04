from dataclasses import dataclass


@dataclass(frozen=True)
class Messages:
    greete: str = "Ого, кто мне написал. Рад видеть! Я SURотзыв, полноценный член команды и бот с душой."
    greete_continues: str = "Давайте немного поболтаем, и вы по секрету расскажите мне," \
                            " как прошла ваша работа с моими коллегами? С вас — 3 минуты свободного" \
                            " времени, с меня — бонус в конце. Ммм?"
    general_information: str = 'Конечно, я вас помню, но для формальности напишите: ' \
                        '✅ имя и фамилию;\n✅ должность;\n✅ название проекта.'
    manager_name: str = 'Как звали менеджера, с которой вы работали? Кстати, я их всех знаю. ' \
                        'А еще мы иногда вместе на обед ходим.'
    rating_manager: str = 'Вам достался суперпрофессионал! И как справилась с работой? Надеюсь, не подвела.'
    review_us = "Ага, тогда предлагаю обсудить немного подробнее. Как прошла работа над проектом? " \
                "Остались какие-то незакрытые вопросы? Мне можно рассказать всё. "
    repeat_chance: str = 'Общаться с вами — одно удовольствие, а расставание — разрыв сердечка. ' \
                         'Придете к нам еще?'
    you_cool_answer: str = 'Если бы мог, осыпал бы вас лепестками роз за такие приятные слова. ' \
                           'А пока хочу еще немного подогреть интерес и познакомить с нашим агентством'
    middling_answer: str = 'Мы вообще такие сальто крутим в сфере рекламы, ооо. ' \
                           'Но к чему слова, когда проще посмотреть'
    shit_answer: str = 'У нас есть кое-что получше любого психолога. ' \
                       'Проверено: убирает тревожность через 3, 2, 1'



services = {'a': 'Таргетированная реклама',
            'b': 'Медийная, контекстная или programmatic реклама',
            'c': 'Работа со СМИ',
            'd': 'Наружная реклама',
            'e': 'Работа с инфлюенсерами',
            'f': 'Услуги по созданию сайта',
            'g': 'Услуги дизайна',
            'h': 'E-mail рассылки',
            'i': 'SMM',
            'j': 'Фото и видеосъемка'}


msg = Messages()
