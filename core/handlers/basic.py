from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from db.queries import queries
from db.models import User
from core.keyboards.keyboards import get_kb_main_menu


async def start_handler(message: types.Message):
    kb = get_kb_main_menu()
    await message.answer('Привет, я бот-напоминалка зарегистрируйся /reg',
                         reply_markup=kb)


async def send_kb_main_menu(message: types.Message):
    kb = get_kb_main_menu()
    await message.answer('Клавиатура создана',
                         reply_markup=kb)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    kb = get_kb_main_menu()
    await message.answer('Операция прервана', reply_markup=kb)
    await state.finish()


async def send_profile(message: types.Message):
    user: User = await queries.select_user(message.chat.id)
    group = await queries.select_groups_for_user(message.chat.id)
    text = f'Ваш профиль:\n' \
           f'ID: {user.telegram_id}\n' \
           f'ФИО: {user.fullname}\n' \
           f'Псевдоним: {user.shortname}\n' \
           f'Группы: {", ".join(group)}'
    if user.photo is not None:
        await message.answer_photo(photo=user.photo, caption=text)
    else:
        await message.answer(text)


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(send_kb_main_menu, commands=['keyboard'])
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')
    dp.register_message_handler(send_profile, Text(startswith='🌝Профиль'))
