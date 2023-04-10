from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from core.keyboards import keyboards
import datetime


class ReminderState(StatesGroup):
    text = State()
    time = State()
    date_send = State()
    date_last = State()
    date_delete = State()
    user = State()
    group = State()
    end_rem = State()


async def reminder_start(message: types.Message):
    await message.answer('Режим создания напоминания, для отмены введите /cancel')
    await ReminderState.text.set()


async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text.strip())
    kb = keyboards.get_kb_back_cancel()
    await message.answer('Хорошо, теперь введите время отправление', reply_markup=kb)
    await ReminderState.next()


async def get_time(message: types.Message, state: FSMContext):
    if await state_back(message, state, text='Введите текст'):
        pass
    else:
        try:
            time = await check_time()
            await state.update_data(time=time)
            time_list = []
            for t in time:
                time_list.append("{}:{}".format(t.hour, t.minute))
            time_str = ', '.join(time_list)
            await message.answer(f'Время: {time_str}, теперь выберите дни отправки напоминания')
        except:
            message.answer('Время введено некорректно')


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await message.answer('Операция прервана')
    await state.finish()


def register_handler(dp: Dispatcher):
    dp.register_message_handler(reminder_start, commands=['start'])


async def state_back(message, state, text):
    if message.text == '⬅️ Назад':
        await message.answer(text)
        await ReminderState.previous()
        return True
    elif message.text == '🚫 Отмена':
        await message.answer('Регистрация прервана')
        await state.finish()
        return True
    else:
        return False


async def check_time(message_text):
    result = []
    list_str = message_text.split()
    for temp in list_str:
        time = datetime.datetime.strptime(f'{temp}', '%H%M')
        result.append(time)
    return result
