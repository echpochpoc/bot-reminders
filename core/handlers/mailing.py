import calendar
import locale
import re
import datetime as dt
import sqlalchemy
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import core.handlers.basic
from core.filters import StateClassFilter
from core.keyboards import *
from core.create_connect import bot
from db.queries import queries
from db import models


async def send_reminder_for_me(message: types.Message):
    reminders = await queries.select_reminders_for_me(telegram_id=message.chat.id)
    if reminders:
        for rem in reminders:
            msg_text = get_msg_text(rem)
            kb = types.InlineKeyboardMarkup().insert(
                InlineKeyboardButton('Выполнить', callback_data=f'rem_done_{rem.id}'))
            await message.answer(f'🟥🟥🟥🟥🟥🟥\n{msg_text}', reply_markup=kb)
    else:
        await message.answer('У вас нет невыполненных напоминаний')


async def send_my_reminder(message: types.Message):
    reminders = await queries.select_my_reminders(telegram_id=message.chat.id)
    if reminders:
        for rem in reminders:
            if rem.status is True:
                users = await queries.select_reminder_users_status(reminder_id=rem.id)
                text = get_msg_text(rem)
                users_str = get_str_users_reminder(users)
                text = text + users_str
                kb = types.InlineKeyboardMarkup().insert(
                    InlineKeyboardButton('Удалить', callback_data=f'rem_delete_{rem.id}'))
                await message.answer(f'🟨🟨🟨🟨🟨🟨\n'
                                     f'{text}',
                                     parse_mode='HTML',
                                     reply_markup=kb)
    else:
        await message.answer('У вас нет активных напоминаний')


async def done_reminder(call: types.CallbackQuery):
    rem_id = int(re.findall(r'\d+', call.data)[0])
    user = await queries.select_user(telegram_id=call.message.chat.id)
    try:
        await queries.update_reminder_status_to_done(reminder_id=rem_id, user_id=user.id)
        await queries.check_reminder_for_completion(reminder_id=rem_id)
        now = datetime.datetime.now()
        time = now.strftime("%d.%m.%y %H:%M:%S")
        text = call.message.text.replace('🟥', '🟩') + f'\nНапоминание выполнено от: {time}'
        await call.message.edit_text(text)
        await call.answer(f'Напоминание №{rem_id} выполнено')
        await send_creator_user_done_reminder(rem_id)
    except sqlalchemy.exc.NoResultFound:
        await call.message.edit_text(f'Напоминание №{rem_id} было удаленно❌')


async def send_creator_user_done_reminder(rem_id):
    user = await queries.select_reminder_creator(reminder_id=rem_id)
    await bot.send_message(chat_id=user.telegram_id,
                           text=f"Пользователь {user.shortname} выполнил напоминание №{rem_id}")


async def delete_reminder(call: types.CallbackQuery):
    rem_id = int(re.findall(r'\d+', call.data)[0])
    try:
        await queries.delete_reminder(rem_id)
    finally:
        pass
    await call.answer(text='Напоминание удалено')
    await call.message.delete()


async def send_reminder_scheduler():
    reminders = await queries.select_reminder_for_send()
    for rem in reminders:
        users = await queries.select_users_for_reminder(reminder_id=rem.id)
        msg_text = get_msg_text(rem)
        kb = types.InlineKeyboardMarkup().insert(
            InlineKeyboardButton('Выполнить', callback_data=f'rem_done_{rem.id}'))
        for user in users:
            await bot.send_message(chat_id=user.telegram_id, text=f'🟥🟥🟥🟥🟥🟥\n{msg_text}', reply_markup=kb)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(send_my_reminder, Text(startswith='⏰Ваши напоминания'))
    dp.register_message_handler(send_reminder_for_me, Text(startswith='📬Напоминания вам'))
    dp.register_callback_query_handler(done_reminder, Text(startswith='rem_done'))
    dp.register_callback_query_handler(delete_reminder, Text(startswith='rem_delete'))


def get_msg_text(rem: models.Reminder) -> str:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    times = ' '.join([t.strftime("%H:%M") for t in rem.times])
    dates = '---'
    if rem.dates:
        dates = ' '.join([d.strftime("%d.%m.%y") for d in rem.dates])
    days_week = '---'
    if rem.days_week:
        days_week = ' '.join([list(calendar.day_abbr)[dw] for dw in rem.days_week])
    date_delete = '---'
    if rem.date_delete:
        date_delete = rem.date_delete.strftime("%d.%m.%y")
    msg_text = f'Напоминание №{rem.id}\n' \
               f'Текст: {rem.text}\n' \
               f'Время: {times}\n' \
               f'Дата: {dates}\n' \
               f'Дни недели: {days_week}\n' \
               f'Дата удаления: {date_delete}\n'
    return msg_text


def get_str_users_reminder(users: list[(str, bool)]) -> str:
    users_no_done = '\nВыполняют⏳:\n'
    users_done = 'Выполнили✅:\n'
    for user in users:
        if user[1] is True:
            users_done += user[0] + ' '
        else:
            users_no_done += user[0] + ' '
    text = f'{users_no_done}\n' \
           f'-------\n' \
           f'{users_done}'
    return text
