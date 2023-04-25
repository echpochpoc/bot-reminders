import re
import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from core.filters.filters import StateClassFilter
from core.keyboards import keyboards
from db.queries import queries
from db.models import Reminder


class ReminderState(StatesGroup):
    text = State()
    times = State()
    dates_send = State()
    days_week = State()
    date_delete = State()
    users = State()
    groups = State()


async def reminder_start(message: types.Message):
    await message.answer('Режим создания напоминания, для отмены введите /cancel')
    await msg_get_text(message)


async def msg_get_text(message: types.Message):
    kb = keyboards.get_kb_back()
    await message.answer('Введите текст напоминания',
                         reply_markup=kb)
    await ReminderState.text.set()


async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text.strip())
    await msg_get_times(message)


async def msg_get_times(message: types.Message):
    await message.answer('Введите время отправление \n'
                         'Например: 1000, 1230 или 2135, несколько значений введите через пробел '
                         'или воспользуйтесь клавиатурой',
                         reply_markup=keyboards.get_clock(hour=9, minute=0))
    await ReminderState.times.set()


async def get_times_call(call: types.CallbackQuery, state: FSMContext):
    hour, minute = map(int, re.findall(r'\d+', call.data))
    times = datetime.time(hour, minute)
    await state.update_data(times=[times])
    await call.answer()
    await msg_get_dates_send(call.message)


async def get_times_str(message: types.Message, state: FSMContext):
    times = check_time(message.text)
    if not times:
        await message.answer('Время введено некорректно')
    else:
        await state.update_data(times=times)
        await msg_get_dates_send(message)


async def msg_get_dates_send(message: types.Message):
    inline_kb = keyboards.get_kb_calendar()
    await message.answer('Даты выбраны: ', reply_markup=inline_kb)
    await ReminderState.dates_send.set()


async def get_dates_send(call: types.CallbackQuery, state: FSMContext):
    if 'cal_day' in call.data:
        text = edit_text_msg_dates_send(text=call.message.text,
                                        call=call.data)
        await call.message.edit_text(text, reply_markup=call.message.reply_markup)
    elif call.data == 'cal_done':
        dates = []
        dates_str = call.message.text.replace('Даты выбраны:', '').split(' ')
        if not (dates_str[0] == ''):
            for date_str in dates_str:
                dates.append(datetime.datetime.strptime(date_str, '%d.%m.%Y'))
        await state.update_data(dates_send=dates)
        await msg_get_days_week(call.message)
    await call.answer()


async def msg_get_days_week(message: types.Message):
    kb = keyboards.get_kb_days_week()
    await message.answer('Выберите дни недели: ', reply_markup=kb)
    await ReminderState.days_week.set()


async def get_days_week(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'days_week_done':
        kb = call.message.reply_markup['inline_keyboard']
        days = keyboards.get_data_on_keyboards(kb)
        await state.update_data(days_week=days)
        await msg_get_date_delete(call.message)
    elif 'days_week' in call.data:
        kb = call.message.reply_markup['inline_keyboard']
        new_kb = keyboards.check_keyboard(kb, call.data)
        await call.message.edit_text(call.message.text, reply_markup=new_kb)
    await call.answer()


async def msg_get_date_delete(message: types.Message):
    await message.answer('Выберите дату удаления напоминания: ',
                         reply_markup=keyboards.get_kb_calendar())
    await ReminderState.date_delete.set()


async def get_date_delete(call: types.CallbackQuery, state: FSMContext):
    if 'cal_day' in call.data:
        date_str = ".".join(re.findall(r'\d+', call.data))
        date = datetime.datetime.strptime(date_str, '%d.%m.%Y')
        await state.update_data(date_delete=date)
    else:
        await state.update_data(date_delete=None)
    await msg_get_users(call.message)
    await call.answer()


async def msg_get_users(message: types.Message):
    kb = keyboards.get_kb_users(await queries.select_user_all())
    await message.answer(f'Выберите пользователей: ', reply_markup=kb)
    await ReminderState.users.set()


async def get_users(call: types.CallbackQuery, state: FSMContext):
    if 'user_ID' in call.data:
        kb = keyboards.check_keyboard(keyboard=call.message.reply_markup['inline_keyboard'],
                                      call=call.data)
        await call.message.edit_text(text=call.message.text, reply_markup=kb)
    elif call.data == 'user_done':
        users = keyboards.get_data_on_keyboards(
            keyboard=call.message.reply_markup['inline_keyboard'])
        await state.update_data(users=users)
        await msg_get_groups(call.message)
    await call.answer()


async def msg_get_groups(message: types.Message):
    kb = keyboards.get_kb_inline_groups(await queries.select_all_groups())
    await message.answer(text='Выберите группы: ', reply_markup=kb)
    await ReminderState.groups.set()


async def get_groups(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'group_done':
        groups = keyboards.get_data_on_keyboards(
            keyboard=call.message.reply_markup['inline_keyboard'])
        await state.update_data(groups=groups)
        await end_rem(call.message, state)
    elif 'group' in call.data:
        kb = keyboards.check_keyboard(keyboard=call.message.reply_markup['inline_keyboard'],
                                      call=call.data)
        await call.message.edit_text(text=call.message.text, reply_markup=kb)


async def end_rem(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        creator = await queries.select_user(telegram_id=message.chat.id)
        reminder = Reminder(
            creator_id=creator.id, text=data['text'],
            date_delete=data['date_delete'], times=data['times'],
            days_week=data['days_week'], dates=data['dates_send'],
        )
        users = await get_set_users(data['users'], data['groups'])
    await queries.insert_reminder(reminder, users)
    await message.answer('Напоминание создано',
                         reply_markup=keyboards.get_kb_main_menu())
    await state.finish()


async def go_back(message: types.message, state: FSMContext):
    function_dict = {
        "ReminderState:text": msg_get_text,
        "ReminderState:times": msg_get_text,
        "ReminderState:dates_send": msg_get_times,
        "ReminderState:days_week": msg_get_dates_send,
        "ReminderState:date_delete": msg_get_days_week,
        "ReminderState:users": msg_get_date_delete,
        "ReminderState:groups": msg_get_users,

    }
    now_state = await state.get_state()
    if now_state in function_dict:
        await function_dict[now_state](message)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(reminder_start, commands=['reminder'])
    dp.register_message_handler(reminder_start, Text(equals='🖊Создать напоминание'))
    dp.register_callback_query_handler(clock_edit, Text(startswith='clock'), state=ReminderState.times)
    dp.register_callback_query_handler(cal_edit, Text(startswith='cal_month'), state='*')
    dp.register_message_handler(go_back, StateClassFilter(state_class='ReminderState'),
                                Text(equals='⬅️Назад'), state='*')

    dp.register_message_handler(get_text, state=ReminderState.text)
    dp.register_message_handler(get_times_str, state=ReminderState.times)
    dp.register_callback_query_handler(get_times_call, Text(startswith='time_done'), state=ReminderState.times)
    dp.register_callback_query_handler(get_dates_send, Text(startswith='cal'), state=ReminderState.dates_send)
    dp.register_callback_query_handler(get_days_week, Text(startswith='days_week'), state=ReminderState.days_week)
    dp.register_callback_query_handler(get_date_delete, Text(startswith='cal'), state=ReminderState.date_delete)
    dp.register_callback_query_handler(get_users, Text(startswith='user'), state=ReminderState.users)
    dp.register_callback_query_handler(get_groups, Text(startswith='group'), state=ReminderState.groups)


def check_time(message_text) -> list[datetime.time]:
    result = []
    list_str = message_text.split()
    for temp in list_str:
        try:
            time = datetime.datetime.strptime(f'{temp}', '%H%M').time()
            result.append(time)
        except ValueError:
            return []
    return result


async def clock_edit(call: types.CallbackQuery):
    hour, minute = map(int, re.findall(r'\d+', call.data))
    time = datetime.time(hour, minute)
    delta = get_timedelta(callback=call.data)
    time = (datetime.datetime.combine(datetime.date.today(), time) + delta).time()
    kb = keyboards.get_clock(hour=time.hour, minute=time.minute)
    await call.message.edit_text(call.message.text, reply_markup=kb)


def get_timedelta(callback) -> datetime.timedelta:
    if 'clock_H' in callback:
        if "clock_H_*+" in callback:
            hour = 4
        elif "clock_H_+" in callback:
            hour = 1
        elif "clock_H_*-" in callback:
            hour = -4
        else:
            hour = -1
        delta = datetime.timedelta(hours=hour)
    else:
        if "clock_M_*+" in callback:
            minute = 15
        elif "clock_M_+" in callback:
            minute = 1
        elif "clock_M_*-" in callback:
            minute = -15
        else:
            minute = -1
        delta = datetime.timedelta(minutes=minute)
    return delta


async def cal_edit(call: types.CallbackQuery):
    date = [int(num) for num in re.findall(r'\d+', call.data)]
    if 'cal_month_next' in call.data:
        if date[0] == 12:
            year = date[1] + 1
            month = 1
        else:
            year = date[1]
            month = date[0] + 1
    else:
        if date[0] == 1:
            year = date[1] - 1
            month = 12
        else:
            year = date[1]
            month = date[0] - 1
    inline_kb = keyboards.get_kb_calendar(year=year, month=month)
    await call.message.edit_text(call.message.text, reply_markup=inline_kb)


def edit_text_msg_dates_send(text: str, call: str) -> str:
    date = ".".join(re.findall(r'\d+', call))
    if date in text:
        text = text.replace(f'{date}', '')
    else:
        text = f'{text} {date}'
    return text


async def get_set_users(users_id: list[int], groups_id: list[int]) -> set:
    users_list = set()
    users_groups = (await queries.select_groups_users(groups_id=groups_id))
    for user in users_groups:
        users_list.add(user.id)
    for user in users_id:
        users_list.add(user)
    return users_list
