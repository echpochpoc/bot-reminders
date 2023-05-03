import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from core import ADMIN_ID
from core.keyboards import keyboards

from db.models import Group
from db.queries import queries


class GroupState(StatesGroup):
    title = State()
    description = State()


async def start_registration_group(message: types.Message) -> None:
    if message.chat.id == int(ADMIN_ID):
        await message.answer('Процесс создания группы, для отмены введите /cancel')
        await msg_get_title(message)
    else:
        await message.answer('У вас нет прав, добавлять новые группы')


async def msg_get_title(message: types.Message) -> None:
    await message.answer('Введите название группы')
    await GroupState.title.set()


async def get_title(message: types.Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.title().strip())
    await msg_get_description(message)


async def msg_get_description(message: types.Message) -> None:
    await message.answer('Введите небольшое описание')
    await GroupState.description.set()


async def get_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.title().strip())
    await complete_registration_group(message, state)


async def complete_registration_group(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        group = Group(
            title=data['title'],
            description=data['description'])
        await queries.insert_group(group)
    kb = keyboards.get_kb_main_menu()
    await message.answer('Группа успешно добавлена, '
                         'для добавление еще одной введите /add_group',
                         reply_markup=kb)
    await state.finish()


async def send_groups(message: types.Message) -> None:
    groups = await queries.select_groups_all()
    if groups:
        for group in groups:
            kb = keyboards.get_inline_kb_group_delete(group.id)
            await message.answer(f'Группа: {group.title}\n'
                                 f'Описание: {group.description}',
                                 reply_markup=kb)
    else:
        message.answer('Групп не найдено, создайте новые /add_group')


async def delete_groups(call: types.CallbackQuery) -> None:
    if call.message.chat.id == int(ADMIN_ID):
        group_id = int(re.findall(r'\d+', call.data)[0])
        await queries.delete_group(group_id=group_id)
        await call.answer('Группа удалена')
        await call.message.delete()
    else:
        call.answer('У вас нет прав удалять группы')


def register_handler(dp: Dispatcher):
    dp.register_message_handler(start_registration_group, commands=['add_group'])
    dp.register_message_handler(send_groups, commands=['send_groups'])
    dp.register_callback_query_handler(delete_groups, Text(startswith='delete_group'))
    dp.register_message_handler(get_title, state=GroupState.title)
    dp.register_message_handler(get_description, state=GroupState.description)
