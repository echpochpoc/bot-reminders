from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton


def get_kb_back_cancel():
    buttons = [
        [
            KeyboardButton(text='⬅️ Назад'),
            KeyboardButton(text='🚫 Отмена')
        ],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons,
                                   resize_keyboard=True, )
    return keyboard


def get_kb_back_done():
    buttons = [
        [
            KeyboardButton(text='⬅️ Назад'),
            KeyboardButton(text='✅ Готово')
        ],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons,
                                   resize_keyboard=True, )
    return keyboard


def get_kb_back_skip_cancel():
    buttons = [
        [
            KeyboardButton(text='⬅️ Назад'),
            KeyboardButton(text='⏭️ Пропустить'),
            KeyboardButton(text='🚫 Отмена')
        ],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons,
                                   resize_keyboard=True, )
    return keyboard


def get_kb_yes_no():
    buttons = [
        [
            KeyboardButton(text='🚫 Нет'),
            KeyboardButton(text='✅ Да')
        ],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons,
                                   resize_keyboard=True)
    return keyboard


def check_keyboard(keyboard, callback_data):
    # Проверяем кнопки на отметку, если ее нет и callback_data совпадают добавляем и не наоборот
    new_keyboard = InlineKeyboardMarkup()
    # Обратите внимание, что полученная клавиатура, это матрица и перебирает ее надо через 2 цикла
    # Но это не всегда так может прилететь и просто список, если кнопки расположены в один ряд
    for row in keyboard:
        for button in row:
            if '✅' not in button['text'] and button['callback_data'] == callback_data:
                button['text'] = '✅'+button['text']
            elif '✅' in button['text'] and button['callback_data'] == callback_data:
                button['text'] = button['text'].replace('✅', '')
        new_keyboard.add(*row)
    return new_keyboard


def get_data_on_keyboard(keyboard):
    # Проверяем кнопки, на нажатие и формируем список должностей
    post_list = []
    for row in keyboard:
        for button in row:
            if '✅' in button['text']:
                post_list.append(button['text'].replace('✅', ''))
    return post_list


def get_kb_inline_groups(list_value):
    buttons = []
    n = 0
    for i in list_value:
        buttons.append(InlineKeyboardButton(text=i, callback_data=f'group_{n}'))
        n += 1
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text='⬅️ Назад', callback_data=f'group_back'),
                 InlineKeyboardButton(text='Готово', callback_data=f'group_done'))

    return keyboard
