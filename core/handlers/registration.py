from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from core.keyboards import get_data_on_keyboard, check_keyboard, get_kb_back_cancel, get_kb_back_skip_cancel
from core.keyboards.registration_kb import get_kb_groups


class Registration(StatesGroup):
    fullname = State()
    shortname = State()
    photo = State()
    groups = State()


async def registration_start(message: types.Message):
    await message.answer('Начат процесс регистрации для отмены нажмите /cancel: \nВведите ФИО:')
    await Registration.fullname.set()


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
        await Registration.next()


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
            await Registration.next()


async def get_photo(message: types.Message, state: FSMContext):
    if await state_back(message, state, text='Введите псевдоним'):
        pass
    else:
        if message.text == '⏭️ Пропустить':
            await message.answer('Фото (нет), выберите группы в которых вы состоите',
                                 reply_markup=types.ReplyKeyboardRemove())
            await message.answer('Выберите группы: ', reply_markup=get_kb_groups())
            await Registration.next()
        else:
            if not message.photo:
                await message.answer('Отправлять можно только, сжатые фотографии')
            else:
                async with state.proxy() as data:
                    data['photo'] = message.photo[-1].file_id
                await message.answer('Выберите группы: ', reply_markup=get_kb_groups())
                await Registration.next()


async def get_groups(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'post_done':
        keyboard = call.message.reply_markup['inline_keyboard']
        post_list = ", ".join(get_data_on_keyboard(keyboard))
        async with state.proxy() as data:
            data['groups'] = post_list
        await call.message.answer(f'Регистрация завершина! Для изменения данных зарегистрируйтесь заново /reg')
        await get_profile(message=call.message, state=state)
        await state.finish()
    elif call.data == 'post_back':
        await Registration.previous()
        await call.message.answer(f'Отправьте фото', reply_markup=get_kb_back_skip_cancel())
    else:
        keyboard = call.message.reply_markup['inline_keyboard']
        new_keyboard = check_keyboard(keyboard, callback_data=call.data)
        await call.message.edit_text(text=call.message.text, reply_markup=new_keyboard)
    await call.answer()


def register_handler(dp: Dispatcher):
    dp.register_message_handler(registration_start, commands=['reg'])
    dp.register_message_handler(get_fullname, state=Registration.fullname)
    dp.register_message_handler(get_shortname, state=Registration.shortname)
    dp.register_message_handler(get_photo, content_types=['photo', 'text'], state=Registration.photo)
    dp.register_callback_query_handler(get_groups, Text(startswith='post'), state=Registration.groups)


async def state_back(message, state, text):
    if message.text == '⬅️ Назад':
        await message.answer(text)
        await Registration.previous()
        return True
    elif message.text == '🚫 Отмена':
        await message.answer('Регистрация прервана')
        await state.finish()
        return True
    else:
        return False


async def get_profile(message: types.Message, state: FSMContext):
    # Вынести в отдельный модуль, сделать выборку из БД
    async with state.proxy() as data:
        text = ('Ваш профиль:\n'
                f'ID: {message.chat.id}\n'
                f'ФИО: {data["fullname"]}\n'
                f'Псевдоним: {data["shortname"]}\n'
                f'Группы: {data["groups"]}')
    try:
        await message.answer_photo(photo=data["photo"], caption=text)
    except:
        await message.answer(text)
