import datetime as dt
import re
import locale
import calendar
import sqlalchemy

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from core.filters.filters import UserIsRegistered
from core.keyboards import keyboards
from core.create_connect import bot

from db.queries import queries
from db import models


async def send_reminder_for_me(message: types.Message) -> None:
    """
    Отправляет напоминания созданные для пользователя
    """
    reminders = await queries.select_reminders_for_me(telegram_id=message.chat.id)
    if reminders:
        for reminder in reminders:
            msg_text = get_msg_text(reminder=reminder)
            kb = keyboards.get_inline_kb_reminder_done(reminder_id=reminder.id)
            await message.answer(f'🟥🟥🟥🟥🟥🟥\n{msg_text}', reply_markup=kb)
    else:
        await message.answer('У вас нет невыполненных напоминаний')


async def send_my_reminder(message: types.Message) -> None:
    """
    Отправляет напоминания созданные пользователем
    """
    reminders = await queries.select_my_reminders(telegram_id=message.chat.id)
    if reminders:
        for reminder in reminders:
            text = await get_msg_with_reminder(reminder=reminder)
            kb = keyboards.get_inline_kb_reminder_delete(reminder_id=reminder.id)
            await message.answer(f'🟨🟨🟨🟨🟨🟨\n'
                                 f'{text}', reply_markup=kb)
    else:
        await message.answer('У вас нет активных напоминаний')


async def send_msg_creator_user_done_reminder(reminder_id: int, user_shortname: str) -> None:
    """
    Отправляет создателю напоминания что, пользователь выполнил напоминание
    """
    creator = await queries.select_creator(reminder_id=reminder_id)
    kb = keyboards.get_inline_kb_reminder_details(reminder_id)
    await bot.send_message(chat_id=creator.telegram_id,
                           text=f"Пользователь {user_shortname} выполнил напоминание №{reminder_id}",
                           reply_markup=kb)


async def done_reminder(call: types.CallbackQuery):
    """
    Делает отметку, что напоминание выполнено
    """
    reminder_id = int(re.findall(r'\d+', call.data)[0])
    user = await queries.select_user(telegram_id=call.message.chat.id)
    try:
        await queries.update_reminder_status_to_done(reminder_id=reminder_id, user_id=user.id)
        await queries.check_reminder_for_completion(reminder_id=reminder_id)
        time = dt.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        text = call.message.text.replace('🟥', '🟩') + f'\nНапоминание выполнено от: {time}'
        await call.message.edit_text(text)
        await send_msg_creator_user_done_reminder(reminder_id, user.shortname)
        await call.answer(f'Напоминание №{reminder_id} выполнено')
    except sqlalchemy.exc.NoResultFound:
        await call.message.edit_text(f'Напоминание №{reminder_id} было удаленно❌')


async def detail_reminder(call: types.CallbackQuery) -> None:
    """
    Показывает дополнительные сведенья о напоминании
    """
    reminder_id = int(re.findall(r'\d+', call.data)[0])
    reminder = await queries.select_reminder(reminder_id)
    text = call.message.text + '\n' + get_msg_text(reminder=reminder)
    await call.message.edit_text(text=text)


async def delete_reminder(call: types.CallbackQuery):
    """
    Удаляет напоминание вместе с сообщением
    """
    rem_id = int(re.findall(r'\d+', call.data)[0])
    try:
        await queries.delete_reminder(rem_id)
    finally:
        pass
    await call.answer(text='Напоминание удалено')
    await call.message.delete()


async def send_reminder_scheduler() -> None:
    """
    Каждую минуту ищет напоминания для отправки пользователям, если есть отправляет
    """
    reminders = await queries.select_reminder_for_send()
    for reminder in reminders:
        msg_text = get_msg_text(reminder)
        kb = keyboards.get_inline_kb_reminder_done(reminder_id=reminder.id)
        users = await queries.select_users_for_reminder(reminder_id=reminder.id)
        for user in users:
            await bot.send_message(chat_id=user.telegram_id,
                                   text=f'🟥🟥🟥🟥🟥🟥\n{msg_text}',
                                   reply_markup=kb)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(send_my_reminder, UserIsRegistered(), Text(startswith='⏰Ваши напоминания'))
    dp.register_message_handler(send_reminder_for_me, UserIsRegistered(), Text(startswith='📬Напоминания вам'))
    dp.register_callback_query_handler(done_reminder, Text(startswith='rem_done'))
    dp.register_callback_query_handler(delete_reminder, Text(startswith='rem_delete'))
    dp.register_callback_query_handler(detail_reminder, Text(startswith='rem_detail'))


def get_msg_text(reminder: models.Reminder) -> str:
    """
    Представляет напоминание в текстовом виде
    """
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    times = ' '.join([t.strftime("%H:%M") for t in reminder.times])
    dates = '---'
    if reminder.dates:
        dates = ' '.join([d.strftime("%d.%m.%y") for d in reminder.dates])
    days_week = '---'
    if reminder.days_week:
        days_week = ' '.join([list(calendar.day_abbr)[dw] for dw in reminder.days_week])
    date_delete = '---'
    if reminder.date_delete:
        date_delete = reminder.date_delete.strftime("%d.%m.%y")
    msg_text = f'Напоминание №{reminder.id}\n' \
               f'Текст: {reminder.text}\n' \
               f'Время: {times}\n' \
               f'Дата: {dates}\n' \
               f'Дни недели: {days_week}\n' \
               f'Дата удаления: {date_delete}\n'
    return msg_text


def get_users_perform_reminder(users: list[(str, bool)]) -> str:
    """
    Формирует текст с пользователями, которые выполняют или выполнили напоминание
    """
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


async def get_msg_with_reminder(reminder: models.Reminder) -> str:
    """
    Подготавливает текст сообщения для отправки, соединяет часть с напоминанием и выполнение пользователями
    """
    users = await queries.select_reminder_users_status(reminder_id=reminder.id)
    users_done_text = get_users_perform_reminder(users)
    reminder_text = get_msg_text(reminder=reminder)
    result = reminder_text + users_done_text
    return result
