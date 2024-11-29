from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


settings_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Задержка между постингом'),
        ],
        [
            KeyboardButton(text='Время нахождения сторис в профиле'),
        ],
        [
            KeyboardButton(text='Количество отметок с одного аккаунта'),
        ],
        [
            KeyboardButton(text='Максимальное количество отметок с одного аккаунта'),
        ],
        [
            KeyboardButton(text='Посмотреть список админов'),
        ],
        [
            KeyboardButton(text='Изменить список админов'),
        ],
        [
            KeyboardButton(text='Посмотреть настройки'),
        ],
    ],
    resize_keyboard=True
)


story_period_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='6 часов'),
        ],
        [
            KeyboardButton(text='12 часов'),
        ],
        [
            KeyboardButton(text='24 часа'),
        ],
        [
            KeyboardButton(text='48 часов'),
        ],
    ],
    resize_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отмена'),
        ],
    ],
    resize_keyboard=True
)
