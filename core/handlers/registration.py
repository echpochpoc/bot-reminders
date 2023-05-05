import re

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from core.config import ADMIN_ID
import core.handlers.basic
from core.filters import StateClassFilter
from core.keyboards import keyboards

from db.queries import queries
from db.models import User


class RegistrationState(StatesGroup):
    fullname = State()
    shortname = State()
    photo = State()
    groups = State()
    end_reg = State()


async def registration_start(message: types.Message) -> None:
    await message.answer('Регистрация, для отмены нажмите /cancel')
    await msg_get_fullname(message)


async def msg_get_fullname(message: types.Message):
    kb = keyboards.get_kb_back()
    await message.answer('Введите ФИО или просто фамилию имя',
                         reply_markup=kb)
    await RegistrationState.fullname.set()


async def get_fullname(message: types.Message, state: FSMContext):
    fullname = message.text.strip().title().split()
    if len(fullname) < 2 or len(fullname) > 3:
        await message.answer('ФИО должно содержать от 2 до 3 слов, введите заново')
    else:
        await state.update_data(fullname=' '.join(fullname))
        await msg_get_shortname(message)


async def msg_get_shortname(message: types.Message):
    await message.answer(f'Введите псевдоним, он должен быть '
                         'коротким(в одно слово) и понятным для других пользователей')
    await RegistrationState.shortname.set()


async def get_shortname(message: types.Message, state: FSMContext):
    shortname = message.text.strip().title().split()
    if len(shortname) != 1:
        await message.answer('Псевдоним должен состоять из одного слова, введите заново')
    else:
        await state.update_data(shortname=shortname[0])
        await msg_get_photo(message)


async def msg_get_photo(message: types.Message):
    kb = keyboards.get_inline_kb_skip()
    await message.answer('Отправьте фото', reply_markup=kb)
    await RegistrationState.photo.set()


async def get_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer('Отправлять можно только, сжатые фотографии')
    else:
        await state.update_data(photo=message.photo[-1].file_id)
        await msg_get_groups(message)


async def skip_photo(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Выбор фото пропущен')
    await call.answer()
    await state.update_data(photo=None)
    await msg_get_groups(call.message)


async def msg_get_groups(message: types.Message):
    kb = keyboards.get_inline_kb_groups(await queries.select_groups_all())
    await message.answer('Выберите группы: ', reply_markup=kb)
    await RegistrationState.groups.set()


async def get_groups(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'group_done':
        keyboard = call.message.reply_markup['inline_keyboard']
        groups = keyboards.get_text_on_buttons(keyboard)
        await state.update_data(groups=groups)
        await complete_registration(call.message, state)
    else:
        keyboard = call.message.reply_markup['inline_keyboard']
        new_keyboard = keyboards.edit_inline_kb(keyboard, call=call.data)
        await call.message.edit_text(text=call.message.text, reply_markup=new_keyboard)
    await call.answer()


async def complete_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = User(
        telegram_id=message.chat.id,
        fullname=data['fullname'],
        shortname=data['shortname'],
        photo=data['photo'],
        telegram_username=message.chat.username,
        telegram_name=f'{message.chat.last_name} {message.chat.first_name}'.strip(),
    )
    await queries.insert_user(user)
    await queries.insert_groups_users(telegram_id=message.chat.id,
                                      titles_groups=data['groups'])
    await core.handlers.basic.send_profile(message)
    kb = keyboards.get_kb_main_menu()
    await message.answer('Регистрация успешно завершена',
                         reply_markup=kb)
    await state.finish()


async def go_back(message: types.message, state: FSMContext):
    function_dict = {
        "RegistrationState:fullname": msg_get_fullname,
        "RegistrationState:shortname": msg_get_fullname,
        "RegistrationState:photo": msg_get_shortname,
        "RegistrationState:groups": msg_get_photo,
    }
    now_state = await state.get_state()
    if now_state in function_dict:
        await function_dict[now_state](message)


async def send_users(message: types.Message) -> None:
    users = await queries.select_users_all()
    if users:
        for user in users:
            kb = keyboards.get_inline_kb_user_delete(user_id=user.id)
            groups = await queries.select_groups_with_user(telegram_id=user.telegram_id)
            text = f'Ваш профиль:\n' \
                   f'ID: {user.telegram_id}\n' \
                   f'ФИО: {user.fullname}\n' \
                   f'Псевдоним: {user.shortname}\n' \
                   f'Группы: {", ".join([group.title for group in groups])}'
            await message.answer(text=text, reply_markup=kb)
    else:
        await message.answer('Пользователей нет')


async def delete_user(call: types.CallbackQuery) -> None:
    if call.message.chat.id == int(ADMIN_ID):
        user_id = int(re.findall(r'\d+', call.data)[0])
        await queries.delete_user(user_id=user_id)
        await call.answer('Пользователь удален')
        await call.message.delete()
    else:
        await call.answer('У вас нет прав удалять пользователей')


def register_handler(dp: Dispatcher):
    dp.register_message_handler(registration_start, commands=['reg'])
    dp.register_message_handler(send_users, commands=['send_users'])
    dp.register_callback_query_handler(delete_user, Text(startswith='delete_user'))
    dp.register_message_handler(go_back, StateClassFilter(state_class='RegistrationState'),
                                Text(equals='⬅️Назад'), state='*')

    dp.register_message_handler(get_fullname, state=RegistrationState.fullname)
    dp.register_message_handler(get_shortname, state=RegistrationState.shortname)
    dp.register_message_handler(get_photo, content_types=['photo'], state=RegistrationState.photo)
    dp.register_callback_query_handler(skip_photo, Text(startswith='skip'), state=RegistrationState.photo)
    dp.register_callback_query_handler(get_groups, Text(startswith='group'), state=RegistrationState.groups)
