from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from core import ADMIN_ID
from core.keyboards.keyboards import get_kb_yes_no

from db.models import Group
from db.queries.queries import insert_group


class GroupState(StatesGroup):
    title = State()
    description = State()
    end = State()


async def start_add_group(message: types.Message):
    if message.chat.id == int(ADMIN_ID):
        await message.answer('Процесс создания группы, для отмены введите /cancel\n'
                             'Введите название группы')
        await GroupState.title.set()
    else:
        await message.answer('У вас нет прав, добавлять новые группы')


async def get_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text.title().strip()
    await message.answer(f'Название группы "{data["title"]}", теперь введите небольшое описание')
    await GroupState.next()


async def get_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text.strip()
    await message.answer(f'Группа: {data["title"]}\n'
                         f'Описание: {data["description"]}\n\n'
                         f'Создать новую группу?',
                         reply_markup=get_kb_yes_no())
    await GroupState.next()


async def end_add_group(message: types.Message, state: FSMContext):
    if message.text == '✅ Да':
        async with state.proxy() as data:
            group = Group(
                title=data['title'],
                description=data['description'])
        try:
            await insert_group(group)
            await message.answer('Группа успешно добавлена, '
                                 'для добавление еще одной введите /add_group',
                                 reply_markup=types.ReplyKeyboardRemove())
        except:
            await message.answer('Ой, что пошло не так, попробуйте еще раз',
                                 reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    elif message.text == '🚫 Нет':
        await message.answer('Процесс создания группы сброшен',
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer('Команда не распознана используйте клавиатуру')


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_add_group, commands=['add_group'])
    dp.register_message_handler(get_title, state=GroupState.title)
    dp.register_message_handler(get_description, state=GroupState.description)
    dp.register_message_handler(end_add_group, state=GroupState.end)
