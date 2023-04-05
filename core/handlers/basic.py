from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext


async def start_handler(message: types.Message):
    await message.answer('Привет, я бот-напоминалка')


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await message.answer('Операция прервана')
    await state.finish()


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')
