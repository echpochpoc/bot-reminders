import calendar
import locale
import re

from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton

import db.models


def get_kb_back() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True).insert(
        KeyboardButton('⬅️Назад'))
    return kb


def get_kb_main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('🖊Создать напоминание'),
        KeyboardButton('📬Напоминания вам'),
        KeyboardButton('⏰Ваши напоминания'),
        KeyboardButton('🌝Профиль'),
        KeyboardButton('🆘Помощь'),
    )
    return kb


def get_inline_skip() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup().insert(
        InlineKeyboardButton(text='Пропустить',
                             callback_data='skip'))
    return kb


def get_kb_back_cancel():
    buttons = [
        [
            KeyboardButton(text='⬅️Назад'),
            KeyboardButton(text='🚫Отмена')
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


def check_keyboard(keyboard: InlineKeyboardButton, call: str) -> InlineKeyboardMarkup:
    # Проверяем кнопки на отметку, если ее нет и callback_data совпадают добавляем и не наоборот
    new_keyboard = InlineKeyboardMarkup()
    # Обратите внимание, что полученная клавиатура, это матрица и перебирает ее надо через 2 цикла
    # Но это не всегда так может прилететь и просто список, если кнопки расположены в один ряд
    for row in keyboard:
        for button in row:
            if '✅' not in button['text'] and button['callback_data'] == call:
                button['text'] = '✅' + button['text']
            elif '✅' in button['text'] and button['callback_data'] == call:
                button['text'] = button['text'].replace('✅', '')
        new_keyboard.add(*row)
    return new_keyboard


def get_text_on_buttons_kb(keyboard: InlineKeyboardMarkup) -> list[str]:
    '''
    Проверяет кнопки с галочкой и возвращает текст с кнопок
    :param keyboard:
    :return:
    '''

    # Проверяем кнопки, на нажатие и формируем список должностей
    result = []
    for row in keyboard:
        for button in row:
            if '✅' in button['text']:
                result.append(button['text'].replace('✅', ''))
    return result


def get_data_on_keyboards(keyboard):
    # Проверяем кнопки, на нажатие и формируем список должностей
    post_list = []
    for row in keyboard:
        for button in row:
            if '✅' in button['text']:
                value = int(re.findall('\d+', button['callback_data'])[0])
                post_list.append(value)
    return post_list


def get_kb_inline_groups(list_value):
    buttons = []
    n = 0
    for i in list_value:
        buttons.append(InlineKeyboardButton(text=i.title, callback_data=f'group_{i.id}'))
        n += 1
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text='Готово', callback_data=f'group_done'))

    return keyboard


def get_kb_calendar(year=int(datetime.now().year),
                    month=int(datetime.now().month)) -> InlineKeyboardMarkup:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    month_list = list(calendar.month_abbr)
    inline_kb = InlineKeyboardMarkup(row_width=7).row()
    inline_kb.insert(InlineKeyboardButton("<<", callback_data=f'cal_month_prev_{month}_{year}'))
    inline_kb.insert(InlineKeyboardButton(f'{month_list[month]} {year}', callback_data='ignore'))
    inline_kb.insert(InlineKeyboardButton(">>", callback_data=f'cal_month_next_{month}_{year}'))
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        inline_kb.row()
        for day in week:
            if day == 0:
                inline_kb.insert(
                    InlineKeyboardButton(" ", callback_data='ignore'))
                continue
            inline_kb.insert(
                InlineKeyboardButton(str(day), callback_data=f'cal_day_{day}_{month}_{year}'))
    inline_kb.insert(InlineKeyboardButton("Готово", callback_data=f'cal_done'))
    return inline_kb


def get_kb_days_week():
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    inline_kb = InlineKeyboardMarkup(row_width=3).row()
    i = 0
    for day in calendar.day_abbr:
        inline_kb.insert(InlineKeyboardButton(day, callback_data=f'days_week_{i}'))
        i += 1
    inline_kb.insert(InlineKeyboardButton('Готово', callback_data=f'days_week_done'))
    return inline_kb


def get_kb_day_delete(year=int(datetime.now().year),
                      month=int(datetime.now().month)) -> InlineKeyboardMarkup:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    month_list = list(calendar.month_abbr)
    inline_kb = InlineKeyboardMarkup(row_width=7).row()
    inline_kb.insert(InlineKeyboardButton("<<", callback_data=f'day_del_prev_month_{year}_{month}'))
    inline_kb.insert(InlineKeyboardButton(f'{month_list[month]} {year}', callback_data='ignore'))
    inline_kb.insert(InlineKeyboardButton(">>", callback_data=f'day_del_next_month_{year}_{month}'))
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        inline_kb.row()
        for day in week:
            if day == 0:
                inline_kb.insert(
                    InlineKeyboardButton(" ", callback_data='ignore'))
                continue
            inline_kb.insert(
                InlineKeyboardButton(str(day), callback_data=f'day_del_done_{year}_{month}_{day}'))
    return inline_kb


def get_kb_users(list_user: list) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup(row_width=3).row()
    for i in list_user:
        i: db.models.User
        inline_kb.insert(InlineKeyboardButton(text=i.shortname, callback_data=f'user_ID_{i.id}'))
    inline_kb.row().insert(InlineKeyboardButton("Готово", callback_data=f'user_done'))
    return inline_kb
