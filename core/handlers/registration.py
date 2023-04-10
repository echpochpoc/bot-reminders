from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import db.queries.queries
from core.keyboards import *
from db.models import User
from db.queries.queries import insert_user, insert_groups_user


class RegistrationState(StatesGroup):
    fullname = State()
    shortname = State()
    photo = State()
    groups = State()
    end_reg = State()


async def registration_start(message: types.Message):
    await message.answer('Начат процесс регистрации для отмены нажмите /cancel: \nВведите ФИО:')
    await RegistrationState.fullname.set()


async def get_fullname(message: types.Message, state: FSMContext):
    fullname_check = message.text.strip().split()
    if len(fullname_check) < 2 or len(fullname_check) > 3:
        await message.answer('ФИО должно содержать от 2 до 3 слов, введите заново')
    else:
        async with state.proxy() as data:
            data['fullname'] = message.text.strip().title()
        await message.answer(f'Ваше ФИО: {data["fullname"]}\nТеперь введите псевдоним, он должен быть '
                             'коротким(в одно слово) и понятным для других пользователей',
                             reply_markup=get_kb_back_cancel())
        await RegistrationState.next()


async def get_shortname(message: types.Message, state: FSMContext):
    if await state_back(message, state, text='Введите ФИО'):
        pass
    else:
        shortname_check = message.text.strip().split()
        if len(shortname_check) != 1:
            await message.answer('Псевдоним должен состоять из одного слова, введите заново')
        else:
            async with state.proxy() as data:
                data['shortname'] = message.text.strip().title()
            await message.answer(f'Ваш псевдоним: {data["shortname"]}\nТеперь отправьте фото',
                                 reply_markup=get_kb_back_skip_cancel())
            await RegistrationState.next()


async def get_photo(message: types.Message, state: FSMContext):
    if await state_back(message, state, text='Введите псевдоним'):
        pass
    else:
        if message.text == '⏭️ Пропустить':
            async with state.proxy() as data:
                data['photo'] = None
            await message.answer('Фото (нет), выберите группы в которых вы состоите',
                                 reply_markup=types.ReplyKeyboardRemove())
            kb = get_kb_inline_groups(await db.queries.queries.select_all_groups())
            await message.answer('Выберите группы: ', reply_markup=kb)
            await RegistrationState.next()
        else:
            if not message.photo:
                await message.answer('Отправлять можно только, сжатые фотографии')
            else:
                async with state.proxy() as data:
                    data['photo'] = message.photo[-1].file_id
                kb = get_kb_inline_groups(await db.queries.queries.select_all_groups())
                await message.answer('Выберите группы: ', reply_markup=kb)
                await RegistrationState.next()


async def get_groups(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'group_done':
        keyboard = call.message.reply_markup['inline_keyboard']
        groups = get_data_on_keyboard(keyboard)
        async with state.proxy() as data:
            data['groups'] = groups
        await call.message.answer(f'Проверьте данные: ', reply_markup=get_kb_back_done())
        await get_profile(message=call.message, state=state)
        await RegistrationState.next()
    elif call.data == 'group_back':
        await RegistrationState.previous()
        await call.message.answer(f'Отправьте фото', reply_markup=get_kb_back_skip_cancel())
    else:
        keyboard = call.message.reply_markup['inline_keyboard']
        new_keyboard = check_keyboard(keyboard, callback_data=call.data)
        await call.message.edit_text(text=call.message.text, reply_markup=new_keyboard)
    await call.answer()


async def check_data(message: types.Message, state: FSMContext):
    if message.text == '✅ Готово':
        async with state.proxy() as data:
            user = User(telegram_id=message.chat.id,
                        fullname=data['fullname'],
                        shortname=data['shortname'],
                        photo=data['photo'],
                        telegram_name=f'{message.chat.first_name} {message.chat.last_name}',
                        telegram_username=message.chat.username)
        await insert_user(user)
        if not not data['groups']:
            await insert_groups_user(message.chat.id, data['groups'])
        await message.answer('Регистрация завершина', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    elif message.text == '⬅️ Назад':
        kb = get_kb_inline_groups(await db.queries.queries.select_all_groups())
        await message.answer('Удаление клавиатуры', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Выберите группы: ', reply_markup=kb)
        await RegistrationState.previous()
    else:
        await message.answer('Команда нераспознана, используйте клавиатуру')


def register_handler(dp: Dispatcher):
    dp.register_message_handler(registration_start, commands=['reg'])
    dp.register_message_handler(get_fullname, state=RegistrationState.fullname)
    dp.register_message_handler(get_shortname, state=RegistrationState.shortname)
    dp.register_message_handler(get_photo, content_types=['photo', 'text'], state=RegistrationState.photo)
    dp.register_callback_query_handler(get_groups, Text(startswith='group'), state=RegistrationState.groups)
    dp.register_message_handler(check_data, state=RegistrationState.end_reg)


async def state_back(message, state, text):
    if message.text == '⬅️ Назад':
        await message.answer(text)
        await RegistrationState.previous()
        return True
    elif message.text == '🚫 Отмена':
        await message.answer('Регистрация прервана')
        await state.finish()
        return True
    else:
        return False


async def get_profile(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = ('Ваш профиль:\n'
                f'ID: {message.chat.id}\n'
                f'ФИО: {data["fullname"]}\n'
                f'Псевдоним: {data["shortname"]}\n'
                f'Группы: {", ".join(data["groups"])}')
    if data['photo'] is not None:
        await message.answer_photo(photo=data["photo"], caption=text)
    else:
        await message.answer(text)
