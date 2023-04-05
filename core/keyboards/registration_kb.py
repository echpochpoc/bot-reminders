from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_kb_groups():
    buttons = [
        [
            InlineKeyboardButton(text="Школы", callback_data='post_1'),
            InlineKeyboardButton(text="Преподаватели", callback_data='post_2'),
            InlineKeyboardButton(text="Молодежь", callback_data='post_3'),
        ],
        [
            InlineKeyboardButton(text='⬅️ Назад', callback_data='post_back'),
            InlineKeyboardButton(text='Подтвердить', callback_data='post_done')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
