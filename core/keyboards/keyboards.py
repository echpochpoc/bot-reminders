import calendar
import locale
import re
import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
                          ReplyKeyboardMarkup, KeyboardButton
from db import models


def get_kb_back() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопкой назад
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True)\
        .insert(KeyboardButton('⬅️Назад'))
    return kb


def get_kb_yes_no() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)\
        .add(KeyboardButton(text='🚫 Нет'),
             KeyboardButton(text='✅ Да'))
    return kb


def get_kb_main_menu() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру главного меню
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('🖊Создать напоминание'),
        KeyboardButton('📬Напоминания вам'),
        KeyboardButton('⏰Ваши напоминания'),
        KeyboardButton('🌝Профиль'),
        KeyboardButton('🆘Помощь'),
    )
    return kb


def get_inline_kb_reminder_done(reminder_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton(text='Выполнить',
                                   callback_data=f'rem_done_{reminder_id}'))
    return kb


def get_inline_kb_reminder_delete(reminder_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton(text='Удалить',
                                   callback_data=f'rem_delete_{reminder_id}'))
    return kb


def get_inline_kb_reminder_details(reminder_id: int) -> InlineKeyboardMarkup:
    """
    Создает кнопку "Подробнее", чтоб узнать детали напоминания
    """
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton(text='Подробнее',
                                   callback_data=f'rem_detail_{reminder_id}'))
    return kb


def get_inline_kb_skip() -> InlineKeyboardMarkup:
    """
    Кнопка пропустить и все)
    """
    kb = InlineKeyboardMarkup().insert(
        InlineKeyboardButton(text='Пропустить',
                             callback_data='skip'))
    return kb


def edit_inline_kb(inline_kb: InlineKeyboardMarkup, call: str) -> InlineKeyboardMarkup:
    """
    Проверяем кнопки на отметку '✅', если её нет - добавляет, если есть - убирает
    """
    new_keyboard = InlineKeyboardMarkup()
    for row in inline_kb:
        new_row = []
        for button in row:
            button: dict
            if '✅' not in button["text"] and button["callback_data"] == call:
                button['text'] = f'✅{button["text"]}'
            elif '✅' in button['text'] and button['callback_data'] == call:
                button['text'] = button['text'].replace('✅', '')
            new_row.append(button)
        new_keyboard.row(*new_row)
    return new_keyboard


def get_text_on_buttons(inline_kb: InlineKeyboardMarkup) -> list[str]:
    """
    Формирует список с текстом кнопок, на который был знак '✅'
    """
    result = []
    for row in inline_kb:
        for button in row:
            button: dict
            if '✅' in button['text']:
                result.append(button['text'].replace('✅', ''))
    return result


def get_data_on_keyboards(inline_kb: InlineKeyboardMarkup) -> list[int]:
    """
    Формирует список с числами(id из базы данных) из callback_data, на который был знак '✅'
    """
    result = []
    for row in inline_kb:
        for button in row:
            button: dict
            if '✅' in button['text']:
                value = int(re.findall(r'\d+', button['callback_data'])[0])
                result.append(value)
    return result


def get_inline_kb_group_delete(group_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton(text='Удалить',
                                   callback_data=f'delete_group_{group_id}'))
    return kb


def get_inline_kb_groups(groups: list[models.Group]) -> InlineKeyboardMarkup:
    """
    Создает inline клавиатуру, для выбора групп
    """
    keyboard = InlineKeyboardMarkup()
    for group in groups:
        keyboard.insert(InlineKeyboardButton(text=group.title, callback_data=f'group_{group.id}'))
    keyboard.row(InlineKeyboardButton(text='Готово', callback_data=f'group_done'))
    return keyboard


def get_kb_calendar(year=int(datetime.datetime.now().year),
                    month=int(datetime.datetime.now().month)) -> InlineKeyboardMarkup:
    """
    Создает интерактивный календарь с возможностью листать месяцы
    """
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    month_list = list(calendar.month_abbr)
    inline_kb = InlineKeyboardMarkup(row_width=7)
    inline_kb.row(InlineKeyboardButton("<<", callback_data=f'cal_month_prev_{month}_{year}'),
                  InlineKeyboardButton(f'{month_list[month]} {year}', callback_data='ignore'),
                  InlineKeyboardButton(">>", callback_data=f'cal_month_next_{month}_{year}'))
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


def get_inline_kb_days_week() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора дня недели,
    в callback указывается номер дня где 0 - понедельник, 6 - воскресенье
    """
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    inline_kb = InlineKeyboardMarkup()
    i = 0
    for day in calendar.day_abbr:
        inline_kb.insert(InlineKeyboardButton(text=day, callback_data=f'days_week_{i}'))
        i += 1
    inline_kb.insert(InlineKeyboardButton('Готово', callback_data=f'days_week_done'))
    return inline_kb


def get_clock(hour: int, minute: int) -> InlineKeyboardMarkup:
    """
    Возвращает inline клавиатуру для выбора времени
    """
    this_time = datetime.time(hour=hour, minute=minute)
    str_hour = this_time.strftime('%H')
    str_minute = this_time.strftime('%M')
    inline_kb = InlineKeyboardMarkup(row_width=4)
    inline_kb.add(InlineKeyboardButton("⏫", callback_data=f'clock_H_*+_{hour}_{minute}'),
                  InlineKeyboardButton("🔼", callback_data=f'clock_H_+_{hour}_{minute}'),
                  InlineKeyboardButton("⏫", callback_data=f'clock_M_*+_{hour}_{minute}'),
                  InlineKeyboardButton("🔼", callback_data=f'clock_M_+_{hour}_{minute}'),)
    inline_kb.add(InlineKeyboardButton(f"{str_hour}", callback_data=f'ignore'),
                  InlineKeyboardButton(f"{str_minute}", callback_data=f'ignore'))
    inline_kb.add(InlineKeyboardButton("⏬", callback_data=f'clock_H_*-_{hour}_{minute}'),
                  InlineKeyboardButton("🔽", callback_data=f'clock_H_-_{hour}_{minute}'),
                  InlineKeyboardButton("⏬", callback_data=f'clock_M_*-_{hour}_{minute}'),
                  InlineKeyboardButton("🔽", callback_data=f'clock_M_-_{hour}_{minute}'))
    inline_kb.insert(InlineKeyboardButton("Готово", callback_data=f'time_done_{hour}_{minute}'))
    return inline_kb


def get_inline_kb_users(users: list[models.User]) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру, для выбора пользователей
    """
    inline_kb = InlineKeyboardMarkup()
    for user in users:
        inline_kb.insert(InlineKeyboardButton(text=user.shortname, callback_data=f'user_{user.id}'))
    inline_kb.row(InlineKeyboardButton("Готово", callback_data=f'user_done'))
    return inline_kb
