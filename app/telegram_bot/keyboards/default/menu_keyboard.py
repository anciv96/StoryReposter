from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='➕ Добавить аккаунт'),
        ],
        [
            KeyboardButton(text='📥 Импорт аккаунтов'),
        ],
        [
            KeyboardButton(text='Просмотр аккаунтов'),
        ],
        [
            KeyboardButton(text='📝 Загрузить список'),
        ],
        [
            KeyboardButton(text='▶️ Начать теггинг'),
        ],
        [
            KeyboardButton(text='⏹️ Остановить теггинг'),
        ],
        [
            KeyboardButton(text='Настройки – Посмотреть текущие настройки и внести изменения'),
        ],
    ],
    resize_keyboard=True
)






